import { useEffect, useMemo, useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useRoomContext,
} from "@livekit/components-react";
import { RoomEvent, Participant } from "livekit-client";

type TaskEvent = {
  type: "task_added";
  title: string;
  desc: string;
  all?: Record<string, string>;
};

function TasksPanel({ tasks }: { tasks: Record<string, string> }) {
  const entries = Object.entries(tasks);
  return (
    <div style={{ padding: 12, border: "1px solid #333", borderRadius: 12 }}>
      <h3 style={{ marginTop: 0 }}>Tasks</h3>
      {entries.length === 0 ? (
        <div>No tasks yet.</div>
      ) : (
        <ul>
          {entries.map(([title, desc]) => (
            <li key={title}>
              <b>{title}</b> — {desc}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function VoiceHUD() {
  const room = useRoomContext();
  const [agentSpeaking, setAgentSpeaking] = useState(false);

  useEffect(() => {
    // active speakers is the easiest “talking indicator”
    const onActiveSpeakersChanged = (speakers: Participant[]) => {
      // heuristic: any remote participant speaking = agent speaking
      const isRemoteSpeaking = speakers.some((p) => !p.isLocal);
      setAgentSpeaking(isRemoteSpeaking);
    };

    room.on(RoomEvent.ActiveSpeakersChanged, onActiveSpeakersChanged);
    return () => {
      room.off(RoomEvent.ActiveSpeakersChanged, onActiveSpeakersChanged);
    };
  }, [room]);

  return (
    <div style={{ padding: 12, border: "1px solid #333", borderRadius: 12 }}>
      <div>
        Agent: <b>{agentSpeaking ? "Speaking…" : "Idle / Listening"}</b>
      </div>

      <div style={{ marginTop: 8 }}>
        <button
          onClick={() => room.localParticipant.setMicrophoneEnabled(true)}
          style={{ marginRight: 8 }}
        >
          Mic On
        </button>
        <button
          onClick={() => room.localParticipant.setMicrophoneEnabled(false)}
        >
          Mic Off
        </button>
      </div>
    </div>
  );
}

function RoomUI() {
  const room = useRoomContext();
  const [tasks, setTasks] = useState<Record<string, string>>({
    "learn Livekit": "need to learn livekit and make something out of it",
  });

  useEffect(() => {
    const onData = (
      payload: Uint8Array,
      participant?: Participant,
      _kind?: any,
      topic?: string,
    ) => {
      if (topic !== "tasks") return;

      try {
        const text = new TextDecoder().decode(payload);
        const evt = JSON.parse(text) as TaskEvent;

        if (evt.type === "task_added") {
          // if agent sends full snapshot, use it; else patch
          if (evt.all) {
            setTasks(evt.all);
          } else {
            setTasks((prev) => ({ ...prev, [evt.title]: evt.desc }));
          }
        }
      } catch (e) {
        console.error("Bad tasks payload", e);
      }
    };

    room.on(RoomEvent.DataReceived, onData);
    return () => {
      room.off(RoomEvent.DataReceived, onData);
    };
  }, [room]);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <VoiceHUD />
        {/* Renders all audio coming from the room (agent voice) */}
        <RoomAudioRenderer />
      </div>

      <TasksPanel tasks={tasks} />
    </div>
  );
}

export default function App() {
  const [connected, setConnected] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [url, setUrl] = useState<string | null>(null);

  const roomName = useMemo(() => "taskmaster-room", []);

  async function connect() {
    try {
      const identity = "web-" + crypto.randomUUID();

      const res = await fetch("http://localhost:8001/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          room: roomName,
          identity,
          name: "Web User",
        }),
      });

      if (!res.ok) {
        throw new Error("Token server error");
      }

      const data = await res.json();

      if (!data.token || !data.url) {
        throw new Error("Invalid token response");
      }

      setToken(data.token);
      setUrl(data.url);
      console.log("url " + data.url);

      setConnected(true);
    } catch (err) {
      console.error("Failed to connect:", err);
      alert("Failed to connect to LiveKit");
    }
  }

  if (!connected) {
    return (
      <div style={{ padding: 24 }}>
        <h2>TaskMaster Voice Agent</h2>
        <button onClick={connect}>Connect</button>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      {url && token && (
        <LiveKitRoom
          serverUrl={url}
          token={token}
          connect={true}
          audio={true}
          video={false}
          onDisconnected={() => setConnected(false)}
        >
          <RoomUI />
        </LiveKitRoom>
      )}
    </div>
  );
}
