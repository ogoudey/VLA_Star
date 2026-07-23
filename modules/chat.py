import socket
import threading
import queue
import time
import os

from setproctitle import setproctitle
setproctitle("vla_chat")


microphone = None
speaker = None

MEDIUM = os.environ.get("MEDIUM", "TYPING")

match MEDIUM:
    case "AUDIO":
        from modules.audio_chat import text_to_speech, play_speech, record_speech, speech_to_text
    case "REALTIME":
        from modules.realtime_audio_chat import start_realtime_transcription
        from modules.audio_chat import text_to_speech, play_speech


def text_text(text):
    print(f"\nRobot: {text}\nReply: ")

def play_text(text):
    speech = text_to_speech(text)
    play_speech(speech)

def read_text():
    return input("Reply: ")

def record_text():
    bytes = record_speech()
    text = speech_to_text(bytes)
    return text

match MEDIUM:
    case "TYPING":
        speech_function = text_text
        listen_function = read_text
    case "AUDIO":
        speech_function = play_text
        listen_function = record_text
    case "REALTIME":
        speech_function = play_text
        listen_function = None

def respond_loop(inbound_q, send_q, stop_event):
    try:
        while not stop_event.is_set():
            msg = inbound_q.get()
            speech_function(msg)
    except Exception as e:
        print(f"Error in respond loop!: {e}")

def reply_loop(send_q, stop_event):
    try:
        while not stop_event.is_set():
            reply = listen_function()
            send_q.put(reply)
    except Exception as e:
        print(f"Error in respond loop!: {e}")

def connect(chat_port):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", chat_port))
            print(f"Connected.")
            return sock
        except ConnectionRefusedError:
            print(f"Waiting on {chat_port}...", end="\r")
            time.sleep(1)

def run_client(chat_port=5001):
    sock = connect(chat_port)
    stop_event = threading.Event()
    inbound_q = queue.Queue()
    send_q = queue.Queue()

    threading.Thread(
        target=chat_utilities.recv_loop,
        args=(sock, inbound_q, stop_event),
        daemon=True
    ).start()

    threading.Thread(
        target=chat_utilities.send_loop,
        args=(sock, send_q, stop_event),
        daemon=True
    ).start()

    threading.Thread(
        target=respond_loop,
        args=(inbound_q, send_q, stop_event),
        daemon=True
    ).start()
    
    if MEDIUM == "REALTIME":
        start_realtime_transcription(send_q)
        
    else:
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
        print("Disconnected. You may close this chat terminal.")
        stop_event.set()
        sock.close()
from vla_star.vla_complex.utilities.chat_core import Router, Conversation, SSHClient, EntryInterface, OutInterface, SecretManager
import getpass
import sys
if __name__ == "__main__":
    router = Router()
    ssh_client = SSHClient()
    interface = OutInterface(router, ssh_client)
    interface.open_new_convo(sys.argv[1], "127.0.0.1", getpass.getuser())
    while True:
        interface.add_to_conversation(input("[...] "))