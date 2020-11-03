import sys

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

from db import redis_cli, influxdb_cli
from conf import conf


def handle():
    ont_conf = conf.get('ont')
    read_length_step = ont_conf.get('read_length_step')
    scan_iter = redis_cli.scan_iter(match='CELL:READ_LEN:*')
    measurement = 'reads_length_stats'
    influxdb_data = []
    for key in scan_iter:
        for k, v in redis_cli.hgetall(key).items():
            barcode, read_len = k.split('_')
            display_read_len = int(read_len) * read_length_step
            data = '%s,%s %s' % (
                measurement,
                'cell=%s,barcode=%s,read_len=%s' % (
                    key[14:],
                    barcode,
                    '%s-%s' % ((read_length_step * (int(read_len) - 1)) + 1, display_read_len),
                ),
                'value=%s' % v
            )
            influxdb_data.append(data)
    influxdb_cli.write_points(points=influxdb_data, protocol='line')


if __name__ == '__main__':
    handle()
