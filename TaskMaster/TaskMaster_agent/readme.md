# 🎙️ TaskMaster

**TaskMaster** is an AI-powered **voice task assistant** built with **LiveKit Agents** and **FastAPI**.  
It allows users to **add, update, and list tasks using their voice in real time**, while syncing task updates to a frontend via LiveKit data channels.

---

## 📌 Overview

Users can say things like:

- “Add a task to learn LiveKit”
- “Update the task learn LiveKit”
- “List my tasks”

---

## 📂 Project Structure

```text
taskmaster/
├── agent.py            # AI voice agent (LiveKit AgentServer)
├── server.py           # FastAPI token + agent dispatch server
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md

```

## 🔐 Environment Variables

```
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
NEXT_PUBLIC_LIVEKIT_URL=
OPENAI_API_KEY=your_openai_key

```

## Create a Virtual Environment

```
python -m venv .venv

```

Activate it with Windows:

```
.venv\Scripts\activate
```

## Install Dependencies

```
pip install -r requirements.txt
```

## Run the AI Voice Agent

```
python agent.py dev
```

## 🌐 Run the FastAPI Server

```
python -m uvicorn token_server:app --port 8001 --reload
```

## 🔌 API Usage

### 🎟️ Create Token & Dispatch Agent

#### POST /token

```
{
  "room": "task-room-1",
  "identity": "user_123",
  "name": "Carl"
}
```

#### Response

```
{
  "room": "task-room-1",
  "identity": "user_123",
  "name": "Carl"
}
```
