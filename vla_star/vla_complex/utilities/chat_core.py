"""
Peer-to-peer messaging over SSH tunnels.

Design notes
------------
Every Agent runs the same process and can play two roles at once:

  * Router       -- passively listens for other Agents that want to talk to
                    *us*. It owns one well-known "rendezvous" port (5001)
                    plus a small pool of "conversation" ports (5002-5004).
  * OutInterface -- actively reaches out to another Agent (identified by a
                    `name` that SecretManager resolves to host/user/password)
                    to *start* a conversation.

No conversation port is ever exposed to the public internet. The only open
door on a remote machine is sshd (22). Everything else -- the 5001
rendezvous call and the actual conversation traffic on 500x -- travels
through an SSH "direct-tcpip" channel, which is paramiko's implementation
of the same trick `ssh -L` / `ssh -W` does. We never bind a local forwarded
port ourselves; we just ask the SSH transport for a channel that behaves
like a socket connected to 127.0.0.1:<port> *on the far end*, tunnelled
through the existing encrypted session. That channel object exposes
.send()/.recv()/.close(), so the rest of the code (Conversation) never has
to know whether it's holding a real socket or an SSH channel.

Wire format: every message (control-plane "give me a port" calls AND
conversation messages) is a 4-byte big-endian length prefix followed by a
UTF-8 JSON payload. Length-prefixing (rather than newline-delimited) is
used because paramiko channels don't guarantee line-buffered delivery the
way a plain TCP stream with readline() might lead you to assume.
"""

import json
import queue
import socket
import struct
import threading
import time
from typing import List, Optional, Callable
import sys
import paramiko
import subprocess
import json
import re
from pathlib import Path
import getpass

# ---------------------------------------------------------------------------
# Wire format helpers -- work identically over socket.socket or paramiko.Channel
# ---------------------------------------------------------------------------

def send_frame(transport, obj) -> None:
    payload = json.dumps(obj).encode("utf-8")
    header = struct.pack(">I", len(payload))
    transport.send(header + payload)

def _recv_exact(transport, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = transport.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("peer closed connection")
        buf += chunk
    return buf


def recv_frame(transport, timeout: Optional[float] = None):
    if timeout is not None and hasattr(transport, "settimeout"):
        transport.settimeout(timeout)
    header = _recv_exact(transport, 4)
    (length,) = struct.unpack(">I", header)
    payload = _recv_exact(transport, length)
    return json.loads(payload.decode("utf-8"))

# ---------------------------------------------------------------------------
class LocalNetworkManager:
    SERVICE = "_bed._tcp"
    LOCAL_MANIFEST = Path.home() / ".vla_stars.jsonl"

    @staticmethod
    def _discover_bed_hosts():
        """
        Browse avahi for _bed._tcp instances and return
        [{"user": ..., "hostname": ..., "address": ...}, ...]
        """
        result = subprocess.run(
            ["avahi-browse", "-rtp", LocalNetworkManager.SERVICE],
            capture_output=True, text=True, timeout=15,
        )

        entries = []
        for line in result.stdout.splitlines():
            if not line.startswith("="):  # "=" = resolved record
                continue
            fields = line.split(";")
            if len(fields) < 10:
                continue

            hostname = fields[6]
            address = fields[7]
            txt = fields[9]

            m = re.search(r'"?username=([^";]*)"?', txt)
            if not m:
                continue

            entries.append({
                "user": m.group(1),
                "hostname": hostname,
                "address": address,
            })

        # de-dupe (multi-interface hosts can show up twice)
        seen = set()
        unique = []
        for e in entries:
            key = (e["user"], e["hostname"])
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique

    @staticmethod
    def _ssh_connect(user: str, hostname: str, address: str | None = None) -> paramiko.SSHClient:
        password = SecretManager.get_ssh_password_for_host(hostname)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=address or hostname,
            username=user,
            password=password,
            timeout=5,
        )
        return client

    @staticmethod
    def _get_manifests_for(user: str, hostname: str, address: str | None = None) -> list[str]:
        """SSH in and list what manifest_consultant.sh offers."""
        try:
            client = LocalNetworkManager._ssh_connect(user, hostname, address)
        except (paramiko.SSHException, OSError):
            return []

        try:
            stdin, stdout, stderr = client.exec_command(
                'bash -l -c "\\"$VLA_STAR_PATH\\"/activation/targets/manifest_consultant.sh"',
                timeout=15,
            )
            output = stdout.read().decode()
        finally:
            client.close()

        return [line.strip() for line in output.splitlines() if line.strip()]

    @staticmethod
    def _get_local_manifests_from_file() -> list[str]:
        """Read this machine's own manifest list from ~/.vla_stars.jsonl."""
        if not LocalNetworkManager.LOCAL_MANIFEST.exists():
            return []

        manifests = []
        with open(LocalNetworkManager.LOCAL_MANIFEST) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # support either {"name": "..."} objects or bare strings per line
                name = entry.get("name") if isinstance(entry, dict) else entry
                if name:
                    manifests.append(name)
        return manifests
    
    @staticmethod
    def get_local_manifests():
        merged = {}

        local_hostname = socket.gethostname()
        local_user = getpass.getuser()
        local_manifests = LocalNetworkManager._get_local_manifests_from_file()
        if local_manifests:
            merged.setdefault(local_hostname, {})[local_user] = local_manifests

        for entry in LocalNetworkManager._discover_bed_hosts():
            hostname, user, address = entry["hostname"], entry["user"], entry["address"]
            manifests = LocalNetworkManager._get_manifests_for(user, hostname, address)
            merged.setdefault(hostname, {})[user] = manifests

        return merged

    @staticmethod
    def get_local_agents():
        merged_manifest = LocalNetworkManager.get_local_manifests()
        agents = [
            item
            for host in merged_manifest.values()
            for user_list in host.values()
            for item in user_list
        ]
        return agents

    @staticmethod
    def get_host_and_user_of_name(name: str):
        local_manifests = LocalNetworkManager.get_local_manifests()
        for hostname, users in local_manifests.items():
            for user, manifests in users.items():
                if name in manifests:
                    return hostname, user
        print(f"[SecretManager] Could not find {name} in any manifests.")

        return None, None

class SecretManager:
    _PATH = "private/secrets/ssh_passwords.json"

    @staticmethod
    def get_ssh_password_for_host_and_user(host: str, user: str) -> dict:
        """
        Expects private/secrets/ssh_passwords.json shaped like:
        {
          "alice-desktop": {"host": "10.0.0.12", "user": "alice", "password": "..."}
        }
        """

        with open(SecretManager._PATH, "r") as f:
            data = json.load(f)
        try:
            return data[host][user]
        except KeyError as e:
            print(f"[SecretManager] Could not find {host}@{user} in .secrets")
            return {}


# ---------------------------------------------------------------------------

class Conversation:
    def __init__(self, position: str, transport=None, interlocutor: Optional[str]="Unknown"):
        self.position = position
        self.transport = transport
        self.interlocutor = interlocutor
        self.outbound: "queue.Queue[str]" = queue.Queue()
        self.inbound: "queue.Queue[str]" = queue.Queue()
        self._closed = False

    def send_message(self):
        match self.position:
            case "client":
                self.send_message_as_client()
            case "server":
                self.send_message_as_server()

    def add_to_conversation(self, text: str):
        """Public entry point: queue a message and push it out immediately."""
        self.outbound.put(text)
        self.send_message()

    def send_message_as_client(self):
        self._flush_outbound()

    def send_message_as_server(self):
        self._flush_outbound()

    def _flush_outbound(self):
        while not self.outbound.empty():
            text = self.outbound.get_nowait()
            send_frame(self.transport, {"type": "text", "text": text})

    def receive_loop_step(self) -> bool:
        """Blocks for exactly one incoming message. Returns False when the
        conversation should end (peer said bye, or the socket died)."""
        try:
            msg = recv_frame(self.transport)
        except (ConnectionError, OSError):
            return False
        if msg.get("type") == "bye":
            return False
        text = msg.get("text", "")
        self.inbound.put(text)
        print(f"[Conversation] [{self.position}] \"{text}\"")
        return True

    def start_receiving_in_background(self):
        def _loop():
            while self.receive_loop_step():
                pass
        t = threading.Thread(target=_loop, daemon=True)
        t.start()
        return t

    def handle_close(self):
        self.inbound.put("bye")
        print(f"[Conversation] [{self.position}] Handling close by responding to 'bye'")
        
    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            send_frame(self.transport, {"type": "bye"})
        except Exception:
            pass
        try:
            self.transport.close()
        except Exception:
            pass
        self.handle_close()


# ---------------------------------------------------------------------------

class Router:
    RENDEZVOUS_PORT = 5005
    BOB_RENDEZVOUS_PORT = 5001
    available_ports: List[int] = [5002, 5003, 5004]

    on_router_conversation: Callable
    stop_responding_bool: threading.Event

    def __init__(self):
        self._lock = threading.Lock()
        self._rendezvous_sock: Optional[socket.socket] = None
        self._stop_flag = threading.Event()
        self.conversation: Optional[Conversation] = None
        self.start_listener()
        self.on_router_conversation = None # initialized by owner
        self.stop_responding_bool = None # initialized by owner

    def start_listener(self):
        """Real TCP listener on 5001. Bound to loopback only -- the outside
        world never talks to this directly, only via an ssh tunnel that
        lands here."""
        self._rendezvous_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._rendezvous_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._rendezvous_sock.bind(("127.0.0.1", self.RENDEZVOUS_PORT))
        except OSError as e:
            print(f"Port already in use: {e}. Two agents live on one host?")
        self._rendezvous_sock.listen(5)
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while not self._stop_flag.is_set():
            try:
                client_sock, addr = self._rendezvous_sock.accept()
            except OSError:
                break  # socket was closed during shutdown
            threading.Thread(
                target=self._handle_rendezvous, args=(client_sock, addr), daemon=True
            ).start()

    def _handle_rendezvous(self, client_sock: socket.socket, addr):
        try:
            request = recv_frame(client_sock, timeout=5)
            if request.get("type") != "request_convo":
                send_frame(client_sock, {"error": "unknown request type"})
                return

            port = self._allocate_port()
            if port is None:
                send_frame(client_sock, {"error": "no conversation ports available"})
                return

            conv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            conv_sock.bind(("127.0.0.1", port))
            conv_sock.listen(1)

            # Tell the caller which port to connect to *before* we block on accept.
            send_frame(client_sock, {"conversation": port})

            threading.Thread(
                target=self._run_conversation_server, args=(conv_sock, port, addr), daemon=True
            ).start()
        except Exception as e:
            print(f"[Router] rendezvous with {addr} failed: {e}")
        finally:
            client_sock.close()

    def _allocate_port(self) -> Optional[int]:
        with self._lock:
            return self.available_ports.pop(0) if self.available_ports else None

    def _release_port(self, port: int):
        with self._lock:
            self.available_ports.append(port)

    def _run_conversation_server(self, conv_sock: socket.socket, port: int, addr):
        conv_sock.settimeout(30)  # give the client 30s to actually connect
        try:
            peer_sock, _ = conv_sock.accept()
        except socket.timeout:
            print(f"[Router] nobody connected on {port}, releasing it.")
            self._release_port(port)
            conv_sock.close()
            return
        
        print("[Router] New convseration started. (I'm server)")
        self.conversation = Conversation("server", transport=peer_sock)
        try:
            self.on_router_conversation()
            print(f"[Router] Called on_router_conversation ({self.on_router_conversation.__name__})")
        except Exception as e:
            print(f"[Router] Could not call `on_router_conversation`: {e}.")
        conversing = True
        try:
            while conversing:
                conversing = self.conversation.receive_loop_step()
        finally:
            peer_sock.close()
            conv_sock.close()
            self._release_port(port)
            print(f"[Router] Ended that conversation with {addr}.")
            self.stop_responding_bool.set()
            self.conversation.handle_close()

    def cancel_any_local_convo(self):
        if self.conversation:
            self.conversation.close()
            self.conversation = None


# ---------------------------------------------------------------------------

class SSHClient:
    """
    Owns one live SSH connection to a remote Agent, and knows how to mint
    direct-tcpip channels (the "tunnel") over it on demand.
    """

    def __init__(self):
        self._ssh: Optional[paramiko.SSHClient] = None
        self._transport: Optional[paramiko.Transport] = None
        self._conversation_channel: Optional[paramiko.Channel] = None

    def connect(self, host: str, user: str, password: str, port: int = 22):
        self._ssh = paramiko.SSHClient()
        # For a closed set of machines you control, pin host keys instead
        # of AutoAddPolicy before this goes anywhere near production.
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(hostname=host, port=port, username=user, password=password, timeout=10)
        self._transport = self._ssh.get_transport()

    def open_channel(self, remote_port: int, timeout: float = 10) -> paramiko.Channel:
        """
        This *is* the ssh tunnel / port-forward. Instead of binding a local
        port and shuttling bytes ourselves, we ask the transport for a
        direct-tcpip channel straight to 127.0.0.1:<remote_port> on the far
        side. The channel quacks like a socket, so callers can .send()/.recv()
        it exactly like the real socket.socket the Router uses.
        """
        if self._transport is None:
            raise RuntimeError("SSHClient is not connected")
        dest_addr = ("127.0.0.1", remote_port)
        local_addr = ("127.0.0.1", 0)
        return self._transport.open_channel("direct-tcpip", dest_addr, local_addr, timeout=timeout)

    def activate_agent_by_name(self, name: str):
        """Runs the wake-up script on the remote machine over the same ssh
        session (exec, not a shell) and waits for it to finish."""
        if self._ssh is None:
            raise RuntimeError("SSHClient is not connected")
        _, stdout, stderr = self._ssh.exec_command(f"activate_vla_star_v1.sh {name}")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            raise RuntimeError(f"activation failed ({exit_status}): {stderr.read().decode()}")

    def cancel_and_disconnect_any_remote_convo(self):
        if self._conversation_channel is not None:
            try:
                self._conversation_channel.close()
            except Exception:
                pass
            self._conversation_channel = None
        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None
            self._transport = None


# ---------------------------------------------------------------------------

class EntryInterface:
    """Speaks to the *remote* Router's rendezvous port (5001) through an
    already-established SSH tunnel."""

    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    def get_conversation_port(self, timeout: float = 5) -> int:
        chan = self.ssh_client.open_channel(Router.RENDEZVOUS_PORT, timeout=timeout)
        try:
            send_frame(chan, {"type": "request_convo"})
            response = recv_frame(chan, timeout=timeout)
        finally:
            chan.close()  # this request channel is one-shot; the real convo gets its own channel

        if "error" in response:
            raise RuntimeError(response["error"])
        return response["conversation"]


class OutInterface:
    router: Router
    ssh_client: SSHClient
    
    def __init__(self, router: Router, ssh_client: SSHClient):
        self.router = router
        self.ssh_client = ssh_client
        self._conversation: Optional[Conversation] = None

    @property
    def conversation(self) -> Conversation:
        if self._conversation is None:
            return self.router.conversation
        else:
            return self._conversation
    @classmethod
    def open_interface(cls):
        r = Router()
        ssh = SSHClient()
        return cls(r, ssh)

    def open_new_convo(self, name: str, host: str, user: str, password: Optional[str]=None):
        if password:
            password = {"password": password}
        else:
            creds = SecretManager.get_ssh_password_by_name(name)
            print(f"[OutInterface] [open_new_convo] Found SSH password: {creds}")
        if self._conversation:
            print(f"[open_new_convo] Closing current conversation with {self._conversation.interlocutor}")
            self._conversation.close()
        self.router.cancel_any_local_convo()
        self.ssh_client.cancel_and_disconnect_any_remote_convo()
        print("[OutInterface] [open_new_convo] Any existing conversations exited.")
        self.ssh_client.connect(host=host, user=user, password=creds["password"])
        print("[OutInterface] [open_new_convo] SSH client connected.")
        entry = EntryInterface(self.ssh_client)
        print("[OutInterface] [open_new_convo] EntryInterface created.")
        try:
            port = entry.get_conversation_port()
            print(f"[OutInterface] [open_new_convo] Got port {port}.")
        except (RuntimeError, ConnectionError, socket.timeout, paramiko.SSHException):
            print(f"[OutInterface] [open_new_convo] Failed to get port.")
            # No one answered on 5001 -- the agent is asleep. Wake it, then retry once.
            self.ssh_client.activate_agent_by_name(name)
            time.sleep(2)  # give the remote listener a moment to bind its socket
            port = entry.get_conversation_port()

        chan = self.ssh_client.open_channel(port)
        self.ssh_client._conversation_channel = chan  # so cancel_and_disconnect can close it later
        print("[OutInterface] [open_new_convo] New conversation started. (I'm client)")
        self._conversation = Conversation("client", transport=chan, interlocutor=name)
        self._conversation.start_receiving_in_background()

    def add_to_conversation(self, text: str):
        if self._conversation is None:
            try:
                self.router.conversation.add_to_conversation(text)
            except Exception:
                print(f"Failed to add_to_conversation...")
                raise RuntimeError("[OutInterface] No open conversation - call open_new_convo(name) first")
        else:
            self._conversation.add_to_conversation(text)