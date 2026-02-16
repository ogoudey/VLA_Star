# =============================
#   Is turned on, uses VAD.
#   With VAD, returns segments.
#
#
#
#
#
#
#

import asyncio
import json
import base64
import os
import websockets
import pyaudio
import threading
import requests
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

### AUDIO SAMPLING CONFIG
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 30
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)

### configure session
url = "https://api.openai.com/v1/realtime/transcription_sessions"
headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

body = {
    "input_audio_format": "pcm16",
    "input_audio_transcription": {
        "model": "gpt-4o-transcribe",
        "language": "en"
    },
    "turn_detection": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 500
    }
}

response = requests.post(url, headers=headers, json=body)

if response.status_code != 200:
    print("Error creating transcription session:", response.text)
    raise RuntimeError("Failed to create session")

session_info = response.json()
print("Created session:", json.dumps(session_info, indent=2))

ephemeral_token = session_info["client_secret"]["value"]
print("Ephemeral token:", ephemeral_token)

WS_URL = "wss://api.openai.com/v1/realtime?intent=transcription"

def start_realtime_transcription(send_q):
    def run_main():
        asyncio.run(async_main(send_q))

    t = threading.Thread(target=run_main, daemon=True)
    t.start()

class RealtimeTranscriber:
    def __init__(self, send_q):
        self.send_q = send_q
        self.ws = None
        self.running = False

    async def connect(self):
        headers = {
            "Authorization": f"Bearer {ephemeral_token}",
            "OpenAI-Beta": "realtime=v1"
        }

        self.ws = await websockets.connect(
            WS_URL,
            additional_headers=headers
        )

    async def send_audio(self):
        print(f"Sending audio...")

        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )

        self.running = True
        chunks_sent = 0
        while self.running:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            encoded = base64.b64encode(data).decode("utf-8")
            chunks_sent += 1
            print(f"Chunks send: {chunks_sent}", end="\r")
            await self.ws.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": encoded
            }))
            await asyncio.sleep(0)

        stream.stop_stream()
        stream.close()
        audio.terminate()

    async def receive_events(self):
        print(f"Receiving events...")
        async for message in self.ws:
            event = json.loads(message)
            event_type = event.get("type")
            print(event)
            match event_type:
                case "transcription_session.created":
                    session = event.get("session", {})
                    print("[session created]", session["id"], "model:", session.get("input_audio_transcription", {}).get("model"))
                case "input_audio_buffer.speech_started":
                    print(f"[speech_started] item {event.get('item_id')} at {event.get('audio_start_ms')}ms")
                case "input_audio_buffer.speech_stopped":
                    print(f"[speech_stopped] item {event.get('item_id')} at {event.get('audio_end_ms')}ms")
                case "input_audio_buffer.committed":
                    print(f"[committed] item {event.get('item_id')}, previous: {event.get('previous_item_id')}")
                case "conversation.item.created":
                    item = event.get("item", {})
                    print(f"[item created] {item['id']}, status: {item.get('status')}, transcript: {item['content'][0].get('transcript')}")
                case "conversation.item.input_audio_transcription.delta":
                    delta = event.get("delta")
                    print(f"[delta] {delta}", "item:", event.get("item_id"))
                case "conversation.item.input_audio_transcription.completed":
                    text = event.get("transcript", "")
                    if text:
                        print(f"[heard] {text}")
                        self.send_q.put(text)

    async def run(self):
        await self.connect()
        send_task = asyncio.create_task(self.send_audio()) 
        print(f"Send_audio task sent off")       
        await self.receive_events()

    def stop(self):
        self.running = False

async def async_main(send_q):
    transcriber = RealtimeTranscriber(send_q)

    await transcriber.connect()

    await asyncio.gather(
        transcriber.send_audio(),
        transcriber.receive_events(),
    )

