#!/usr/bin/python3
from common import STEP, R_STEP, BaseCommand


class OutputReadsCommand(BaseCommand):
    def parser(self):
        parser = super(OutputReadsCommand, self).parser()
        return parser

    def handle(self, args):
        rc = self.redis_cli()
        ic = self.influxdb_cli()
        scan_iter = rc.scan_iter(match='CELL:*')
        measurement = 'reads_depth_stat'
        for key in scan_iter:
            for k, v in rc.hgetall(key).items():
                position, barcode, read_len = k.split('_')
                display_read_len = int(read_len) * R_STEP
                influxdb_data = '%s,%s %s' % (
                    measurement,
                    'cell=%s,barcode=%s,read_len=%s,position=%05d' % (
                        key[5:],
                        barcode,
                        '%s-%s' % (display_read_len, display_read_len + R_STEP - 1),
                        int(position) * STEP
                    ),
                    'value=%s' % v
                )
                ic.write_points(points=influxdb_data, protocol='line')


if __name__ == '__main__':
    command = OutputReadsCommand()
    command.run()
