from dotenv import load_dotenv
load_dotenv()

import json
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io, function_tool
from livekit.plugins import noise_cancellation, silero

from livekit.plugins import (
    openai,
    noise_cancellation,
)

class Assistant(Agent):
    def __init__(self, tools):
        super().__init__(
            instructions=(
                "You are TaskMaster, a helpful voice assistant.\n"
                "Your job is to create tasks from the user's voice.\n"
                "When the user asks to add a task, call add_task(title, desc).\n"
                "When the user asks to list tasks, call display_tasks()."
            ),
            tools=tools,
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    # ✅ per-session task store
    tasks: dict[str, str] = {
        "learn Livekit": "need to learn livekit and make something out of it"
    }

    room: rtc.Room = ctx.room

    @function_tool
    async def add_task(title: str, desc: str) -> str:
        tasks[title] = desc

        payload = json.dumps({
            "type": "task_added",
            "title": title,
            "desc": desc,
            "all": tasks,  # send full snapshot
        }).encode("utf-8")

        # ✅ publish to frontend
        await room.local_participant.publish_data(
            payload,
            reliable=True,
            topic="tasks",
        )

        return f"Added task: {title}"
    
    @function_tool
    async def update_task(
        current_title: str,
        new_title: str | None = None,
        new_desc: str | None = None,
    ) -> str:
        """Update an existing task's title and/or description."""

        if current_title not in tasks:
            return f"Task '{current_title}' not found."

        # Get old description
        old_desc = tasks[current_title]

        # Determine updated values
        final_title = new_title or current_title
        final_desc = new_desc or old_desc

        # If title changes, remove old key
        if final_title != current_title:
            del tasks[current_title]

        tasks[final_title] = final_desc

        # (Optional) broadcast update to frontend
        payload = json.dumps({
            "type": "task_updated",
            "oldTitle": current_title,
            "title": final_title,
            "desc": final_desc,
            "all": tasks,
        }).encode("utf-8")

        await room.local_participant.publish_data(
            payload,
            reliable=True,
            topic="tasks",
        )

        return f"Updated task '{current_title}'."


    @function_tool
    async def display_tasks() -> str:
        if not tasks:
            return "No tasks yet."
        lines = [f"- {k}: {v}" for k, v in tasks.items()]
        return "Here are your tasks: " + " | ".join(lines)

    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm="openai/gpt-4o-mini",
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        vad=silero.VAD.load(),
    )

    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(
    #         voice="coral"
    #     )
    # )

    await session.start(
        room=room,
        agent=Assistant([add_task, display_tasks,update_task]),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. Speak in English."
    )

if __name__ == "__main__":
    agents.cli.run_app(server)
