import queue
import time
import base64
import wave
import io
from pathlib import Path
import pyaudio
import queue
import io
import os
import numpy as np
import scipy.io.wavfile
from openai import OpenAI # for tts
openai_client = OpenAI()
import numpy as np
import asyncio
from pydub import AudioSegment
from pydub.playback import play
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

if os.environ.get("MEDIUM", "") == "AUDIO":
    import sounddevice as sd

def text_to_speech(text, voice: str = "coral") -> bytes:
    """
    Convert text to speech using OpenAI TTS.
    Returns audio bytes (MP3).
    """
    if text == "":
        return None
    client = OpenAI()

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        speed=0.9,
    ) as response:
        return response.read()

def play_speech(audio_bytes: bytes):
    """
    Play MP3 or WAV audio bytes.
    """
    if audio_bytes is None:
        return
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    play(audio)

def record_speech(duration=5, sample_rate=44100):
    """
    Record audio from mic for `duration` seconds,
    and return WAV bytes (16-bit PCM).
    """
    input("\"\" to talk")
    print(f"Recording {duration}s of audio…")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()

    mem = io.BytesIO()
    scipy.io.wavfile.write(mem, sample_rate, audio)
    mem.seek(0)
    return mem.read()

def speech_to_text(audio_bytes: bytes):
    # Uses gpt-4o-mini-transcribe to output diarized json of speaker-text
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "input.wav"  # name helps certain client libs

    result = openai_client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
        response_format="text",
        chunking_strategy="auto",
    )
    return result.rstrip("\n")

def text_to_speech_generate(text: str):
    """
    Generate speech audio from text using OpenAI TTS.
    Returns: (pcm16_bytes, sample_rate)
    """

    response = openai_client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        format="wav",  # important: easy to decode
    )

    # response.audio is base64-encoded WAV
    wav_bytes = base64.b64decode(response.audio)

    # Decode WAV header → PCM
    pcm_bytes, sample_rate = wav_bytes_to_pcm16(wav_bytes)

    return pcm_bytes, sample_rate

def wav_bytes_to_pcm16(wav_bytes: bytes):
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        assert wf.getsampwidth() == 2  # PCM16
        pcm = wf.readframes(wf.getnframes())
        sample_rate = wf.getframerate()
    return pcm, sample_rate

def respond_loop(inbound_q, send_q, stop_event):
    try:
        while not stop_event.is_set():
            msg = inbound_q.get()

            if msg is None:
                continue

            # TTS (not implemented)
            text_to_speech(msg)

    except Exception as e:
        print(f"Error in respond loop!: {e}")

def reply_loop(send_q, stop_event):
    p = pyaudio.PyAudio()

    try:
        while not stop_event.is_set():
            audio_bytes = record_while_spacebar(p)

            if not audio_bytes:
                continue

            # ASR (not implemented)
            text = speech_to_text(audio_bytes)

            if text:
                send_q.put(text)

    except Exception as e:
        print(f"Error in reply loop!: {e}")

    finally:
        p.terminate()
    

def run_client(chat_port=5001):
    print(f"Opened chat client on {chat_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", chat_port))

    stop_event = threading.Event()
    inbound_q = queue.Queue()
    send_q = queue.Queue()

    threading.Thread(
        target=recv_loop,
        args=(sock, inbound_q, stop_event),
        daemon=True
    ).start()

    threading.Thread(
        target=send_loop,
        args=(sock, send_q, stop_event),
        daemon=True
    ).start()

    threading.Thread(
        target=respond_loop,
        args=(inbound_q, send_q, stop_event),
        daemon=True
    ).start()
    
    threading.Thread(
        target=reply_loop,
        args=(send_q, stop_event),
        daemon=True
    ).start()
    

    
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        sock.close()

# ============== Audio stuff ================ #

def record_while_spacebar(pyaudio_instance):
    frames = []
    recording = threading.Event()

    def on_press(key):
        if key == keyboard.Key.space:
            recording.set()

    def on_release(key):
        if key == keyboard.Key.space:
            recording.clear()
            return False  # stop listener

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Wait for spacebar press
    recording.wait()

    stream = pyaudio_instance.open(
        format=AUDIO_FORMAT,
        channels=AUDIO_CHANNELS,
        rate=AUDIO_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )

    while recording.is_set():
        frames.append(stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False))

    stream.stop_stream()
    stream.close()
    listener.join()

    return b"".join(frames)

def play_pcm16(
    pcm: np.ndarray | bytes,
    sample_rate: int,
    channels: int = 1,
):
    if isinstance(pcm, np.ndarray):
        pcm = pcm.astype(np.int16).tobytes()

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        output=True,
    )

    stream.write(pcm)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    try:
        import sys
        if len(sys.argv) > 1:
            run_client(int(sys.argv[1]))
        else:
            run_client()
    except OSError:
        print("Failed to run client. Make sure a Chat is beginning to listen/listening.")

