# FastAPI Hexagonal Architecture (Ports & Adapters) Blueprint

This repository is a boilerplate project illustrating how to implement Hexagonal Architecture (also known as Ports and Adapters) in Python using FastAPI.

## What is Hexagonal Architecture?

Hexagonal Architecture is a design pattern aimed at creating loosely coupled application components that can be easily connected to their software environment via ports and adapters. This makes components simple to test and easy to swap.

The application is structured into three main layers:

```
                  +-----------------------------------+
                  |           Infrastructure          |
                  |  +-----------------------------+  |
                  |  |         Application         |  |
                  |  |  +-----------------------+  |  |
                  |  |  |         Domain        |  |  |
                  |  |  |                       |  |  |
                  |  |  +-----------------------+  |  |
                  |  +-----------------------------+  |
                  +-----------------------------------+
```

1. **Domain**: The core business logic and rules. It has absolutely no external dependencies (no frameworks, no databases). It defines the entities and the **Ports** (interfaces) for communicating with the outer world.
2. **Application**: Coordinates use cases, orchestrating domain logic and port interactions. It sits on top of the Domain and is driven by inbound clients (e.g., HTTP controllers).
3. **Infrastructure**: Implementations of the ports defined in the Domain layer (Adapters) such as database drivers, external API clients (LLMs, payment gateways), and web interfaces (FastAPI routes and servers).

---

## Directory Structure

*   `domain/`: Core entities and interfaces.
    *   `domain/models/`: Pure domain entities (e.g., chat models).
    *   `domain/ports/`: Interfaces that adapters must implement (e.g., repositories, chat services).
*   `application/`: Orchestration and use cases.
    *   `application/use_cases/`: Implements the flow for specific actions (e.g., handling a chat prompt).
    *   `application/dto/`: Simple data structures to transfer data across layers.
*   `infrastructure/`: Web frameworks, databases, and third-party integrations.
    *   `infrastructure/adapters/`: Implementations of domain ports (e.g., `DummyLLM`, `InMemoryRepository`).
    *   `infrastructure/web/`: FastAPI app, routers, and request/response validation schemas.

---

## Getting Started

### 1. Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Running the Server

To start the FastAPI server:
```bash
uvicorn infrastructure.web.main:app --reload
```

The API documentation will be available at:
*   Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

### Chat Endpoint
*   **POST** `/chat`
    *   Sends a message to the assistant and receives a response.
    *   *Payload:*
        ```json
        {
          "session_id": "optional-uuid-or-string",
          "message": "Hello, how are you?"
        }
        ```
    *   *Response:*
        ```json
        {
          "session_id": "some-session-id",
          "response": "Hello! I am a helper bot from your FastAPI Hexagonal architecture app."
        }
        ```
