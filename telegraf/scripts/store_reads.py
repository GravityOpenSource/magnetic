#!/usr/bin/python3
import json
import math
import re
import sys

from common import STEP, R_STEP, BaseCommand


class StoreReadsCommand(BaseCommand):
    def parser(self):
        parser = super(StoreReadsCommand, self).parser()
        return parser

    def handle(self, args):
        for line in sys.stdin.readlines():
            if not line:
                break
            else:
                self.insert_data(json.loads(line).get('metrics'))

    def insert_data(self, data):
        rc = self.redis_cli()
        for item in data:
            params = item.get('fields')
            params.update(item.get('tags'))
            path = params.get('path')
            pattern = re.compile(r'.*/(.*)/annotations/.*')
            match = re.match(pattern, path)
            cell_name = match.groups()[0]
            start = params.get('start_coords')
            if start == 0:
                continue
            end = params.get('end_coords')
            barcode = params.get('barcode')
            if start % STEP == 0 and start != 0:
                r_start = int(start / STEP) - 1
            else:
                r_start = math.floor(start / STEP)
            r_end = math.ceil(end / STEP)
            read_len = math.ceil(params.get('read_len') / R_STEP)
            for i in range(r_start, r_end):
                for ii in range(0, read_len):
                    key = '%s_%s_%s' % (i, barcode, ii)
                    print(key)
                    rc.hincrby('CELL:%s' % cell_name, key)


if __name__ == '__main__':
    command = StoreReadsCommand()
    command.run()


f=open('a')
f.write()