import asyncio
import random
import uuid
from collections import deque
from datetime import datetime
from typing import Any, AsyncGenerator, Callable

from app.core.config import settings
from app.core.database import open_db_session
from app.models.order import Order


async def get_random_open_port(
    port_start: int = int(settings.port_range_start),
    port_end: int = int(settings.port_range_end),
    local_address: str = settings.local_address,
) -> int:
    while True:
        port = random.randint(port_start, port_end)
        try:
            server = await asyncio.start_server(lambda r, w: None, local_address, port)
            server.close()
            await server.wait_closed()
            return port
        except OSError:
            continue


class Forwarder:
    def __init__(
        self, client_name: str, response_queue: deque[str], connection_timeout: int
    ) -> None:
        self._client_name = client_name
        self._connection_timeout = connection_timeout
        self._connection_future: asyncio.Future[
            tuple[asyncio.StreamReader, asyncio.StreamWriter]
        ] | None = None
        self.response_queue = response_queue

    def _log(self, msg: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.response_queue.append(f"[{timestamp}] {msg}")

    async def _log_custom_messages(self, port: int) -> None:
        username = await self.get_client_username()
        for message in settings.get_custom_messages():
            self._log(message.format(username=username, port=port))

    async def _connection_handler(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        if self._connection_future and not self._connection_future.done():
            self._connection_future.set_result((reader, writer))

    async def _create_server(
        self, port: int | None = None
    ) -> tuple[asyncio.Server, int]:
        if port is None:
            port = await get_random_open_port()

        server = await asyncio.start_server(
            self._connection_handler, settings.local_address, port
        )
        return server, port

    async def _wait_for_connection(
        self,
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Wait for a connection without accessing protected members"""
        self._connection_future = asyncio.Future()

        try:
            return await self._connection_future
        finally:
            self._connection_future = None

    async def relay(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, direction: str
    ) -> None:
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
    ) -> None:
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

    async def start(self, job_id: str, jobs: dict) -> None:
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

    async def get_client_username(self) -> str:
        db_session = await open_db_session()
        try:
            if record := await db_session.get(Order, self._client_name):
                return record.username if record and record.username else "<unknown>"
            return "<unknown>"
        finally:
            await db_session.close()

    async def _handle_connection(self, port: int) -> None:
        db_session = await open_db_session()
        try:
            if record := await db_session.get(Order, self._client_name):
                record.port = int(port)
                await db_session.commit()
        finally:
            await db_session.close()

    async def _handle_disconnection(self) -> None:
        db_session = await open_db_session()
        try:
            if record := await db_session.get(Order, self._client_name):
                await db_session.delete(record)
                await db_session.commit()
        finally:
            await db_session.close()


class ForwarderManager:
    def __init__(self) -> None:
        self._forwarders: dict[str, Forwarder] = {}

    async def create_forwarder(
        self, client_name: str, connection_timeout: int = 120
    ) -> tuple[str, Callable]:
        response_queue: deque[str] = deque()
        forwarder = Forwarder(client_name, response_queue, connection_timeout)
        forwarder_id = str(uuid.uuid4().hex)
        self._forwarders[forwarder_id] = forwarder
        return forwarder_id, forwarder.start

    async def get_forwarder_responses(
        self, forwarder_id: str
    ) -> AsyncGenerator[str, None]:
        forwarder = self._forwarders.get(forwarder_id)
        if forwarder:
            while forwarder_id in self._forwarders:
                if forwarder.response_queue:
                    message = forwarder.response_queue.popleft()
                    yield f"data: {message}\n\n"
                else:
                    await asyncio.sleep(0.1)
            # Send a final message indicating the stream is closing
            yield "data: [STREAM_END]\n\n"

    def is_forwarder_running(self, forwarder_id: str) -> bool:
        return forwarder_id in self._forwarders

    def cancel_forwarder(self, forwarder_id: str) -> bool:
        if forwarder_id in self._forwarders:
            forwarder = self._forwarders[forwarder_id]
            forwarder.response_queue.append("Forwarder cancelled by server")
            del self._forwarders[forwarder_id]
            return True
        return False

    def get_forwarder(self, forwarder_id: str) -> Forwarder | None:
        return self._forwarders.get(forwarder_id)

    @property
    def forwarders(self) -> dict[str, Forwarder]:
        return self._forwarders


forwarder_manager = ForwarderManager()
