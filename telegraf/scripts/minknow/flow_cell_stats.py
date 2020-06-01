#!/usr/bin/python3

import os
import sys

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

import minknow.rpc.manager_pb2 as manager_pb2
import minknow.rpc.manager_pb2_grpc as manager_pb2_grpc
import minknow.rpc.device_pb2 as device_pb2
import minknow.rpc.device_pb2_grpc as device_pb2_grpc

import grpc

from common import BaseCommand


class FlowCellStatsCommand(BaseCommand):
    def parser(self):
        parser = super(FlowCellStatsCommand, self).parser()
        parser.add_argument('-m', '--minknow-hosts', help='minknow hosts', required=True)
        return parser

    def handle(self, args):
        hosts = set(args.minknow_hosts.split(','))
        for host in hosts:
            devices = self.get_devices(host)
            for device in devices.active:
                channel = grpc.insecure_channel('%s:%s' % (host, device.ports.insecure_grpc))
                stub = device_pb2_grpc.DeviceServiceStub(channel)
                device_request = device_pb2.GetFlowCellInfoRequest()
                flow_cell_info = stub.get_flow_cell_info(device_request)
                if flow_cell_info.has_flow_cell:
                    print('flow_cell_info,machine=P1,device=%s,product_code=%s flow_cell_id="%s"' % (
                        device.name,
                        flow_cell_info.product_code,
                        flow_cell_info.flow_cell_id,
                    ))

    def get_devices(self, host):
        manager_stub = self.manager_stub(host)
        list_devices_request = manager_pb2.ListDevicesRequest()
        list_devices_response = manager_stub.list_devices(list_devices_request)
        return list_devices_response

    def manager_stub(self, host):
        manager_channel = grpc.insecure_channel('%s:9501' % host)
        manager_stub = manager_pb2_grpc.ManagerServiceStub(manager_channel)
        return manager_stub


if __name__ == '__main__':
    command = FlowCellStatsCommand()
    command.run()
