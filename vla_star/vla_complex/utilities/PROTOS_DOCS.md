In project root, do:
```
python -m grpc_tools.protoc   -I./vla_star/vla_complex/utilities/unity_protos   --python_out=./vla_star/vla_complex/utilities/generated   --grpc_python_out=./vla_star/vla_complex/utilities/generated   ./vla_star/vla_complex/utilities/unity_protos/unity.proto
```
and
```
protoc   -I./vla_star/vla_complex/utilities/unity_protos   --csharp_out=$HOME/Unity/PolicyClient/Assets/Scripts/Generated   --grpc_out=$HOME/Unity/PolicyClient/Assets/Scripts/Generated   --plugin=protoc-gen-grpc=/home/olin/Unity/PolicyClient/Packages/Grpc.Tools.2.81.0/tools/linux_x64/grpc_csharp_plugin   ./vla_star/vla_complex/utilities/unity_protos/unity.proto
```
