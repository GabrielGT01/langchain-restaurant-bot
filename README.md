# 🍽️ Theo — Restaurant Chatbot

> A production-grade, LLM-powered restaurant assistant built with LangChain, LangGraph, SQLite, Streamlit, Docker, and deployed to AWS EC2.

---

## Assignment 3B — Task Completion Summary

| Task | Status |
|---|---|
| LangChain-powered chatbot with conversation memory and tool use | ✅ Completed |
| Containerized with Docker — runs with a single `docker run` command | ✅ Completed |
| System diagram | ✅ Completed |
| Stretch Goal — Deployed to AWS EC2 with a live URL | ✅ Completed |
| Streaming responses (SSE / WebSocket) | ⚪ Not implemented |
| Gradio frontend | ⚪ Streamlit used instead |

---

## Overview

Theo is a fully deployable restaurant chatbot that acts as a virtual host. Guests can ask about the menu, check opening hours, make reservations, check reservation status, and cancel bookings — all through natural conversation.

The chatbot is backed by a real SQLite database and uses LangChain tool-calling so the LLM never guesses — it always queries live data before responding.

---

## System Diagram

```
User (Browser)
      |
      v
Streamlit UI (port 8501)
      |
      v
LangGraph Agent Loop
      |
      v
ChatOpenAI — gpt-4.1-nano
      |
      +-----------+-----------+-----------+-----------+
      |           |           |           |           |
      v           v           v           v           v
 menu_prices  opening_   table_      check_      cancel_
              hours_tool reservation reservation reservation
      |           |           |           |           |
      +-----------+-----------+-----------+-----------+
                              |
                              v
                      SQLite Database
                      (restaurant_database.db)
                      ┌─────────────────┐
                      │ menu            │
                      │ opening_hours   │
                      │ reservation     │
                      └─────────────────┘
                              |
                              v
                    Tool result returned to LLM
                              |
                              v
                    Natural language response
                              |
                              v
                         User (Browser)
```

---

## Task 1 — LangChain Chatbot with Conversation Memory and Tool Use ✅

### Conversation Memory

Conversation memory is implemented using **LangGraph's `MemorySaver`** checkpointer. Every conversation is assigned a unique `session_id` (UUID) at startup. The full message history is stored and passed to the LLM on every turn, giving Theo genuine multi-turn memory within a session.

```python
from langgraph.checkpoint.memory import MemorySaver

graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": session_id}}
app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
```

### Tool Use

Five tools are registered with the LLM using LangChain's `@tool` decorator and bound via `.bind_tools()`. The LLM decides which tool to call and with what arguments — routing is never hardcoded.

| Tool | Purpose | DB Operation |
|---|---|---|
| `menu_prices` | Returns menu items, descriptions, and prices by category | `SELECT` from `menu` |
| `opening_hours_tool` | Returns opening and closing times for any day | `SELECT` from `opening_hours` |
| `table_reservation` | Creates a new reservation | `INSERT` into `reservation` |
| `check_reservation` | Looks up existing reservations by name | `SELECT` from `reservation` |
| `cancel_reservation` | Cancels a reservation by name | `UPDATE` on `reservation` |

### Agent Loop

Built using **LangGraph `StateGraph`** with a `reason → act → reason` loop:

```
agent_reason → should_continue → act (ToolNode) → agent_reason → END
```

The agent keeps looping until the LLM produces a response with no tool calls, at which point it returns the final message to the user.

### Pydantic Output Schemas

Every tool returns a structured Pydantic model rather than raw text, ensuring the LLM always receives clean, typed data:

- `FoodAgentResponse` — menu results with item list and descriptions
- `OpeningHoursResponse` — hours with day, open, close, and note
- `ReservationAgentResponse` — reservation details with status

### System Prompt

The system prompt defines Theo's persona and enforces strict tool-calling rules — the LLM is explicitly instructed never to assume missing reservation fields (name, year, month, day, time) and to always collect them from the guest before calling any reservation tool.

---

## Task 2 — Docker Containerisation ✅

The full application runs with a **single `docker run` command**:

```bash
docker run -d \
  --name restaurant-bot \
  -p 8501:8501 \
  --env-file .env \
  -v /home/ec2-user/restaurant-bot/db:/app/db \
  --restart unless-stopped \
  025066244860.dkr.ecr.us-east-1.amazonaws.com/restaurant-bot:latest
```

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p db
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Key containerisation decisions

**Single-file architecture** — the entire application (`app.py`) is self-contained with no subfolder imports, making the Docker build straightforward and portable.

**Database baked out, not in** — `restaurant_database.db` is excluded from the image via `.dockerignore`. The `init_db()` function runs on startup, creates the database, and seeds it from in-memory dicts — but only if the tables are empty. This means a mounted volume preserves data across container restarts.

**Secrets at runtime** — the `OPENAI_API_KEY` is never baked into the image. It is injected at runtime via `--env-file .env`, which is also excluded from the image via `.dockerignore`.

**Persistent volume** — the `-v` flag mounts a folder from the host machine into `/app/db` inside the container, so the SQLite database (including all reservations) survives container restarts and image updates.

**Auto-restart** — `--restart unless-stopped` ensures the container comes back up automatically after an EC2 reboot or crash.

### .dockerignore

```
.env
__pycache__
*.pyc
*.pyo
restaurant_database.db
.ipynb_checkpoints
*.ipynb
```

---

## Task 3 — Stretch Goal: AWS EC2 Deployment ✅

The chatbot is deployed and publicly accessible at:

**`http://54.82.24.237:8501`**

### Deployment Stack

| Component | Detail |
|---|---|
| Cloud provider | AWS |
| Compute | EC2 — Amazon Linux 2, t3.micro |
| Container registry | AWS ECR (Elastic Container Registry) |
| Region | us-east-1 |
| Port | 8501 (Streamlit) |
| Database persistence | Docker volume mounted to EC2 disk |
| Secret management | `.env` file on EC2, injected at runtime |

### Deployment Pipeline

```
Local laptop
    │
    ├── docker build -t restaurant-bot .
    ├── docker tag restaurant-bot:latest  →  ECR URI
    └── docker push  →  ECR

ECR (025066244860.dkr.ecr.us-east-1.amazonaws.com/restaurant-bot)
    │
    └── docker pull  →  EC2 instance
            │
            └── docker run -d -p 8501:8501 --env-file .env -v db:/app/db
                        │
                        └── Streamlit app live at http://54.82.24.237:8501
```

---

## Project Structure

```
restaurant-bot/
├── app.py                  # Single-file application — UI, agent, tools, DB all in one
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build instructions
├── .dockerignore           # Excludes .env and DB from image
└── .env                    # Local only — never committed or pushed
```

---

## Database Schema

Three tables in a single `restaurant_database.db` SQLite file:

```sql
-- Menu items by category
CREATE TABLE menu (
    category    TEXT,
    item_name   TEXT,
    description TEXT,
    price       REAL
);

-- Opening hours Mon-Sun
CREATE TABLE opening_hours (
    days  TEXT,
    Open  TEXT,
    close TEXT,
    note  TEXT
);

-- Guest reservations
CREATE TABLE reservation (
    reservation_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT,
    last_name       TEXT,
    year            INTEGER,
    month           INTEGER,
    day             INTEGER,
    time            TEXT,
    status          TEXT   -- 'confirmed' or 'cancelled'
);
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI `gpt-4.1-nano` |
| Agent framework | LangGraph `StateGraph` |
| Tool calling | LangChain `@tool` + `.bind_tools()` |
| Memory | LangGraph `MemorySaver` |
| Output validation | Pydantic v2 `BaseModel` |
| Database | SQLite3 |
| Frontend | Streamlit |
| Containerisation | Docker |
| Registry | AWS ECR |
| Hosting | AWS EC2 (t3.micro) |

---

## Running Locally

**Prerequisites:** Python 3.11+, Docker, an OpenAI API key.

```bash
# 1. Clone the repo
git clone https://github.com/your-username/restaurant-bot.git
cd restaurant-bot

# 2. Create .env
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 3. Run with Docker
docker build -t restaurant-bot .
docker run -p 8501:8501 --env-file .env restaurant-bot

# 4. Open browser
# http://localhost:8501
```

---

## What Theo Can Do

- **Menu** — "What's on the menu?", "What desserts do you have?", "How much is the risotto?"
- **Hours** — "Are you open Sunday?", "What time do you close Friday?"
- **Reservations** — "I'd like to book a table for Saturday at 7pm"
- **Check booking** — "Can you check my reservation?"
- **Cancel booking** — "I need to cancel my reservation"

---

## Notes

- Streamlit was chosen over Gradio as the frontend — it provides an equivalent interactive chat interface with a cleaner UX for this use case.
- Streaming responses were not implemented in this iteration. The agent returns complete responses after the full tool-calling loop completes.
