import grpc
from concurrent import futures
from vla_star.vla_complex.utilities.generated import unity_pb2, unity_pb2_grpc

PROTO_VERSION = "1.0.0"

class UnityInterface:
    def __init__(self, host, port):
        print(f"[UnityInterface] Trying to create grpc channel at {f"{host}:{port}"}.")
        channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = unity_pb2_grpc.AnimateServiceStub(channel)
        print("[UnityInterface] Initializing animation service.")

        version = self.stub.GetVersion(unity_pb2.VersionRequest())
        if version.proto_version != PROTO_VERSION:
            raise RuntimeError(
                f"[UnityInterface] Version mismatch: client={PROTO_VERSION}, server={version.proto_version}"
            )
        
        
    def act(self, action):
        response = self.stub.Act(unity_pb2.ActRequest(action_name=action))
        print("[UnityInterface] Success:", response.success, "Message:", response.message)
        return response.message