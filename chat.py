import socket
import threading
import queue
import time
from chat_utils import recv_line, recv_loop, send_loop
import os



microphone = None
speaker = None

MEDIUM = os.environ.get("MEDIUM", "TEXT")

if MEDIUM == "AUDIO":
    from audio_chat import text_to_speech, play_speech, record_speech, speech_to_text

def text_text(text):
    print(f"\nRobot: {text}\nReply: ")

def play_text(text):
    speech = text_to_speech(text)
    play_speech(speech)

def read_text():
    return input("\nReply: ")

def record_text():
    bytes = record_speech()
    text = speech_to_text(bytes)
    return text

match MEDIUM:
    case "TEXT":
        speech_function = text_text
        listen_function = read_text
    case "AUDIO":
        speech_function = play_text
        listen_function = record_text

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

if __name__ == "__main__":
    try:
        import sys
        if len(sys.argv) > 1:
            run_client(int(sys.argv[1]))
        else:
            run_client()
    except OSError:
        print("Failed to run client. Make sure a Chat is beginning to listen/listening.")
