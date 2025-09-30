import asyncio
import random
import uuid
from collections import deque
from datetime import datetime
from typing import AsyncGenerator

from app.core.config import settings
from app.core.database import open_db_session
from app.models.order import Order


async def get_random_open_port(
    port_start=int(settings.port_range_start),
    port_end=int(settings.port_range_end),
    local_address=settings.local_address,
):
    while True:
        port = random.randint(port_start, port_end)
        try:
            server = await asyncio.start_server(lambda r, w: None, local_address, port)
            server.close()
            await server.wait_closed()
            return port
        except OSError:
            continue


class ForwarderManager:
    def __init__(self):
        self._jobs = {}

    async def create_job(self, client_name, connection_timeout=120):
        response_queue = deque()
        forwarder = Forwarder(client_name, response_queue, connection_timeout)
        job_id = str(uuid.uuid4().hex)
        self._jobs[job_id] = {"response_queue": response_queue}
        return job_id, forwarder.start

    async def get_job_updates(self, job_id: str) -> AsyncGenerator[str, None]:
        job = self._jobs.get(job_id)
        if job:
            while job_id in self._jobs:
                if job["response_queue"]:
                    message = job["response_queue"].popleft()
                    yield f"data: {message}\n\n"
                else:
                    await asyncio.sleep(0.1)
            # Send a final message indicating the stream is closing
            yield "data: [STREAM_END]\n\n"

    def is_job_running(self, job_id: str) -> bool:
        return job_id in self._jobs

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job["response_queue"].append("Job cancelled by server")
            del self._jobs[job_id]
            return True
        return False

    def get_job(self, job_id: str):
        return self._jobs.get(job_id)

    @property
    def jobs(self):
        return self._jobs


class Forwarder:
    def __init__(
        self, client_name: str, response_queue: deque, connection_timeout: int
    ):
        self._client_name = client_name
        self._response_queue = response_queue
        self._connection_timeout = connection_timeout
        self._connection_future = None

    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._response_queue.append(f"[{timestamp}] {msg}")

    async def _log_custom_messages(self, port):
        username = await self.get_client_username()
        for message in settings.custom_messages:
            self._log(message.format(username=username, port=port))

    async def _connection_handler(self, reader, writer):
        if self._connection_future and not self._connection_future.done():
            self._connection_future.set_result((reader, writer))

    async def _create_server(self, port=None):
        if port is None:
            port = await get_random_open_port()

        server = await asyncio.start_server(
            self._connection_handler, settings.local_address, port
        )
        return server, port

    async def _wait_for_connection(self):
        """Wait for a connection without accessing protected members"""
        self._connection_future = asyncio.Future()

        try:
            return await self._connection_future
        finally:
            self._connection_future = None

    async def relay(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, direction: str
    ):
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    self._log(f"{direction}: connection closed")
                    break
                self._log(f"{direction}: {len(data)} bytes")
                writer.write(data)
                await writer.drain()
        except Exception as e:
            self._log(f"{direction} relay error: {e}")
        finally:
            try:
                writer.write_eof()
            except (AttributeError, OSError):
                pass
            writer.close()
            await writer.wait_closed()

    async def handle_connection(
        self,
        source_reader: asyncio.StreamReader,
        source_writer: asyncio.StreamWriter,
        target_reader: asyncio.StreamReader,
        target_writer: asyncio.StreamWriter,
    ):
        try:
            source_to_target = asyncio.create_task(
                self.relay(source_reader, target_writer, "source->target")
            )
            target_to_source = asyncio.create_task(
                self.relay(target_reader, source_writer, "target->source")
            )

            await asyncio.wait(
                [source_to_target, target_to_source],
                return_when=asyncio.FIRST_COMPLETED,
            )

        finally:
            source_to_target.cancel()
            target_to_source.cancel()

            for writer in [source_writer, target_writer]:
                writer.close()
                await writer.wait_closed()

    async def start(self, job_id: int, jobs: dict):
        source_server = None
        target_server = None

        try:
            source_server, source_port = await self._create_server()
            target_server, target_port = await self._create_server()

            await self._handle_connection(target_port)
            self._log(
                f"waiting for connection from {self._client_name} port: {target_port}"
            )

            target_reader, target_writer = await asyncio.wait_for(
                self._wait_for_connection(), timeout=self._connection_timeout
            )

            self._log(f"{self._client_name} connected.")
            self._log(f"waiting for connection from client port: {source_port}")
            await self._log_custom_messages(source_port)

            source_reader, source_writer = await asyncio.wait_for(
                self._wait_for_connection(), timeout=self._connection_timeout
            )

            source_addr = source_writer.get_extra_info("peername")
            self._log(f"client connected from: {source_addr}")

            await self.handle_connection(
                source_reader, source_writer, target_reader, target_writer
            )

        except asyncio.TimeoutError:
            self._log("Connection timeout")
        except Exception as e:
            self._log(f"Error: {e}")
        finally:
            if source_server:
                source_server.close()
                await source_server.wait_closed()
            if target_server:
                target_server.close()
                await target_server.wait_closed()

            self._log("Connection closed")
            await self._handle_disconnection()
            self._log("disconnect")
            if job_id in jobs:
                del jobs[job_id]

    async def get_client_username(self):
        db_session = await open_db_session()
        try:
            if record := await db_session.get(Order, self._client_name):
                return record.username if record and record.username else "<unknown>"
            return "<unknown>"
        finally:
            await db_session.close()

    async def _handle_connection(self, port):
        db_session = await open_db_session()
        try:
            if record := await db_session.get(Order, self._client_name):
                record.port = int(port)
                await db_session.commit()
        finally:
            await db_session.close()

    async def _handle_disconnection(self):
        db_session = await open_db_session()
        try:
            if record := await db_session.get(Order, self._client_name):
                await db_session.delete(record)
                await db_session.commit()
        finally:
            await db_session.close()


forwarder_manager = ForwarderManager()
