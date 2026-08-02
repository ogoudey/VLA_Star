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