import grpc
from concurrent import futures
import numpy as np
from PIL import Image as PILImage
import io
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

    def get_entities(self) -> list[dict]:
        response = self.stub.GetEntities(unity_pb2.GetEntitiesRequest())
        return [
            {
                "id": e.id,
                "name": e.name,
                "type": e.type,
                "position": (e.position.x, e.position.y, e.position.z),
                "rotation_euler": (e.rotation_euler.x, e.rotation_euler.y, e.rotation_euler.z),
                "metadata": dict(e.metadata),
            }
            for e in response.entities
        ]

    def get_observation(self) -> dict:
        response = self.stub.GetObservation(unity_pb2.GetObservationRequest())

        images = {
            name: self._decode_image(img)
            for name, img in response.images.items()
        }
        state = {
            name: np.array(arr.data, dtype=np.float32).reshape(arr.shape)
            for name, arr in response.state.items()
        }
        scalars = dict(response.scalars)

        return {
            "images": images,
            "state": state,
            "scalars": scalars,
            "timestamp_ms": response.timestamp_ms,
        }

    def navigate_to(self, entity_id: str, destination: tuple[float, float, float], speed: float = 0.0) -> bool:
        x, y, z = destination
        response = self.stub.NavigateTo(
            unity_pb2.NavigateToRequest(
                entity_id=entity_id,
                destination=unity_pb2.Vector3(x=x, y=y, z=z),
                speed=speed,
            )
        )
        if not response.success:
            print(f"[navigate_to] failed: {response.message}")
        return response.success

    @staticmethod
    def _decode_image(img_proto) -> np.ndarray:
        if img_proto.encoding in ("png", "jpeg"):
            pil_img = PILImage.open(io.BytesIO(img_proto.data))
            return np.array(pil_img)
        elif img_proto.encoding == "raw_rgb8":
            arr = np.frombuffer(img_proto.data, dtype=np.uint8)
            return arr.reshape(img_proto.height, img_proto.width, img_proto.channels)
        else:
            raise ValueError(f"Unknown image encoding: {img_proto.encoding}")