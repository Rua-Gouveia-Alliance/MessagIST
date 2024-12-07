#!/bin/bash
python -m grpc_tools.protoc -Icontract --python_out=contract/target --pyi_out=contract/target --grpc_python_out=contract/target contract/MessagISTServer.proto
