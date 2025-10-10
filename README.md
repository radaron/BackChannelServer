# BackChannel Server

BackChannel is a web application what provides centralized remote control for connected clients, and monitors their status in real-time.

### Screenshots

![BackChannel Server Interface](doc/images/Screenshot%202025-10-10%20at%2016-17-09%20BackChannel%20Server.png)

![BackChannel Dashboard](doc/images/Screenshot%202025-10-10%20at%2016-18-26%20BackChannel%20Server.png)

### Architecture
```mermaid
architecture-beta
    group server[Server]
    group client[Client]
    group backlink_server[BackLink] in server

    service laptop(server)[Laptop]
    service http_port(server)[http port] in server
    service forwarding_port1(server)[forwarding port] in server
    service forwarding_port2(server)[forwarding port] in server
    service web_app(server)[WebApp] in backlink_server
    service forwarder(server)[Forwarder] in backlink_server
    service blacklink_client(server)[BlackLink] in client
    service ssh_port(server)[SSH port] in client

    laptop:R --> L:http_port
    laptop:B --> L:forwarding_port1
    http_port:R --> L:web_app
    forwarding_port1:R --> L:forwarder
    forwarder:R <--> L:forwarding_port2
    forwarding_port2:R <--> L:blacklink_client
    blacklink_client:R <--> L:ssh_port

```


Sequence of monitoring:
```mermaid
sequenceDiagram
    actor User
    participant Server
    participant Client
    loop 30 sec
        Client->>Server: Get order
        activate Server
        Server-->>Client: Return empty
        deactivate Server
        Client->>Server: Put metrics
    end
    User->>Server: Get all client data
    activate Server
    Server-->>User: return
    deactivate Server
```


Sequence of connecting:
```mermaid
sequenceDiagram
    actor User
    participant Server
    participant Client
    Client->>Server: Get order
    activate Server
    Server-->>Client: Return empty
    Client->>Server: Put metrics
    deactivate Server
    User->>Server: Initiate connection
    activate Server
    Client->>Server: Get order
    activate Server
    Server-->>Client: Return opened port
    deactivate Server
    Client->>Server: Connect to opened port
    Server-->>User: Return opened port
    User<<->>Client: Two way connection
    deactivate Server
```

## Getting started

### Generate Secret Key

Pull the latest docker image:

```bash
docker pull ghcr.io/radaron/backchannel:latest
```

Or use docker-compose:

```yaml
version: '3.8'
services:
  backchannel:
    image: ghcr.io/radaron/backchannel:latest
    ports:
      - "8000:8000"
      - 20000-20100:20000-20100
    environment:
      - SECRET_KEY=your-secret-key
      - MASTER_PASSWORD_HASH=your-master-password-hash
      - ALLOWED_ORIGINS=*
    volumes:
      - ./data:/app/data
```



For production deployment, you need to generate a secure secret key:

```bash
make generate-secret
```

This will generate a UUID-based secret key that you should set in your environment.
### Generate Password Hash

```bash
make hash-password
```
The script will prompt you to enter a password and return a base64-encoded bcrypt hash. Set this in your environment.

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js 18+ (for frontend development)
- Docker or OCI-compatible container runtime

### Development Setup

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Generate security credentials:**
   ```bash
   # Generate a secret key
   make generate-secret

   # Generate password hash
   make hash-password
   ```

3. **Set up environment:**
   ```bash
   cp backchannel.env.example backchannel.env
   # Edit backchannel.env with your generated credentials
   ```

4. **Build frontend and run the application:**
   ```bash
   make up
   ```

5. **Access the application:**
   - http://localhost:8000

## Configuration

Configuration can be customized via environment variables or the `backchannel.env` file:

- `SECRET_KEY` - Session secret key (required for production)
- `MASTER_PASSWORD_HASH` - Hashed master password (preferred over plain text)
- `SESSION_EXPIRE_MINUTES` - Session expiration time (default: 60 minutes)
- `COOKIE_NAME` - Session cookie name (default: backchannel_session)
- `ALLOWED_ORIGINS` - CORS allowed origins (default: "*")
- `PORT_RANGE_START` - Start of port range for dynamic forwarding (default: 20000)
- `PORT_RANGE_END` - End of port range for dynamic forwarding (default: 20100)
- `LOCAL_ADDRESS` - Local address to bind (default: "0.0.0.0")
- `CUSTOM_MESSAGES` - Custom connection instructions (default provided)
