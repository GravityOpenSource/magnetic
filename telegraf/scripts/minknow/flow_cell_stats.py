#!/usr/bin/env python3

import sys

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

import minknow.rpc.manager_pb2 as manager_pb2
import minknow.rpc.manager_pb2_grpc as manager_pb2_grpc
import minknow.rpc.device_pb2 as device_pb2
import minknow.rpc.device_pb2_grpc as device_pb2_grpc
import minknow.rpc.protocol_pb2 as protocol_pb2
import minknow.rpc.protocol_pb2_grpc as protocol_pb2_grpc

import grpc
from grpc._channel import _InactiveRpcError
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
                running = self.get_protocol_running_status(host, device)
                channel = grpc.insecure_channel('%s:%s' % (host, device.ports.insecure_grpc))
                stub = device_pb2_grpc.DeviceServiceStub(channel)
                device_request = device_pb2.GetFlowCellInfoRequest()
                flow_cell_info = stub.get_flow_cell_info(device_request)
                if flow_cell_info.has_flow_cell:
                    if running:
                        status = 2
                    else:
                        status = 3
                else:
                    status = 1
                print('flow_cell_info,machine=P1,device=%s status=%s,product_code="%s",flow_cell_id="%s",x=%s,y=%s' % (
                    device.name,
                    status,
                    flow_cell_info.product_code,
                    flow_cell_info.flow_cell_id,
                    device.layout.x,
                    device.layout.y
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

    def get_protocol_running_status(self, host, device):
        channel = grpc.insecure_channel('%s:%s' % (host, device.ports.insecure_grpc))
        stub = protocol_pb2_grpc.ProtocolServiceStub(channel)
        request = protocol_pb2.GetRunInfoRequest()
        try:
            info = stub.get_current_protocol_run(request)
            if info.run_id:
                return True
            else:
                return False
        except _InactiveRpcError as e:
            if not e.details() == 'No protocol running':
                raise e
            return False


if __name__ == '__main__':
    command = FlowCellStatsCommand()
    command.run()
