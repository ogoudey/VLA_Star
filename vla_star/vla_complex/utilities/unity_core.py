import grpc
from concurrent import futures
from vla_star.vla_complex.utilities.generated import unity_pb2, unity_pb2_grpc

PROTO_VERSION = "1.0.0"

class UnityInterface:
    def __init__(self):
        channel = grpc.insecure_channel("localhost:50051")  # wherever Unity's server listens
        self.stub = unity_pb2_grpc.AnimateServiceStub(channel)

        # Optional handshake: confirm Unity's proto version matches before sending real calls
        version = self.stub.GetVersion(unity_pb2.VersionRequest())
        if version.proto_version != PROTO_VERSION:
            raise RuntimeError(
                f"Version mismatch: client={PROTO_VERSION}, server={version.proto_version}"
            )
        
    def act(self, action):
        response = self.stub.Act(unity_pb2.ActRequest(action_name=action))
        print("Success:", response.success, "Message:", response.message)
        return response.message