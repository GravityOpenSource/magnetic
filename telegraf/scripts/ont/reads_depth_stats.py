import sys

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

from common import BasicCommand
from conf import conf


class ReadsDepthStatsCommand(BasicCommand):
    def handle(self, args):
        ont_conf = conf.get('ont')
        depth_position_step = ont_conf.get('depth_position_step')
        depth_read_length_step = ont_conf.get('depth_read_length_step')
        rc = self.redis_cli()
        ic = self.influxdb_cli()
        scan_iter = rc.scan_iter(match='CELL:DEPTH:*')
        measurement = 'reads_depth_stats'
        influxdb_data = []
        for key in scan_iter:
            for k, v in rc.hgetall(key).items():
                position, barcode, read_len = k.split('_')
                display_read_len = int(read_len) * depth_read_length_step
                data = '%s,%s %s' % (
                    measurement,
                    'cell=%s,barcode=%s,read_len=%s,position=%05d' % (
                        key[11:],
                        barcode,
                        '%s-%s' % (display_read_len, display_read_len + depth_read_length_step - 1),
                        int(position) * depth_position_step
                    ),
                    'value=%s' % v
                )
                influxdb_data.append(data)
        ic.write_points(points=influxdb_data, protocol='line')


if __name__ == '__main__':
    command = ReadsDepthStatsCommand()
    command.run()
