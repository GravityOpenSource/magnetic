#!/usr/bin/python3

import os
import sys

sys.path.append('/opt/grpc')
sys.path.append('../')

import minknow.rpc.protocol_pb2 as protocol
import minknow.rpc.protocol_pb2_grpc as protocol_grpc
import minknow.rpc.manager_pb2 as manager
import minknow.rpc.manager_pb2_grpc as manager_grpc
import minknow.rpc.device_pb2 as device_pb2
import minknow.rpc.device_pb2_grpc as device_pb2_grpc

import grpc

from common import BaseCommand


class FlowCellStatsCommand(BaseCommand):
    def parser(self):
        parser = super(FlowCellStatsCommand, self).parser()
        return parser

    def handle(self, args):
        manager_channel = grpc.insecure_channel('11.11.11.146:9501')
        manager_stub = manager_grpc.ManagerServiceStub(manager_channel)

        list_devices_request = manager.ListDevicesRequest()
        list_devices_response = manager_stub.list_devices(list_devices_request)

        for device in list_devices_response.active:
            print("Found device %s using gRPC port %s" % (device.name, device.ports.insecure_grpc))
            channel = grpc.insecure_channel('11.11.11.146:%s' % device.ports.insecure_grpc)
            stub = device_pb2_grpc.DeviceServiceStub(channel)
            device_request = device_pb2.GetFlowCellInfoRequest()
            print(stub.get_flow_cell_info(device_request))


if __name__ == '__main__':
    command = FlowCellStatsCommand()
    command.run()
