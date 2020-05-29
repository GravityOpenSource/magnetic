#!/usr/bin/python3
import json
import math
import re
import sys

from common import POSITION_STEP, LENGTH_STEP, BaseCommand


class ReadsToRedisCommand(BaseCommand):
    def parser(self):
        parser = super(ReadsToRedisCommand, self).parser()
        return parser

    def handle(self, args):
        for line in sys.stdin.readlines():
            if not line:
                break
            else:
                try:
                    self.insert_data(json.loads(line).get('metrics'))
                except Exception as e:
                    self.logger.info(e)

    def insert_data(self, data):
        rc = self.redis_cli()
        for item in data:
            params = item.get('fields')
            params.update(item.get('tags'))
            path = params.get('path')
            pattern = re.compile(r'[/\w+-]+/([\w-]+)/\w+\.csv')
            match = re.match(pattern, path)
            if not match:
                exit(200)
            cell_name = match.groups()[0]
            start = params.get('start_coords')
            if start == 0:
                continue
            end = params.get('end_coords')
            barcode = params.get('barcode')
            if start % POSITION_STEP == 0 and start != 0:
                r_start = int(start / POSITION_STEP) - 1
            else:
                r_start = math.floor(start / POSITION_STEP)
            r_end = math.ceil(end / POSITION_STEP)
            read_len = math.ceil(params.get('read_len') / LENGTH_STEP)
            for i in range(r_start, r_end):
                for ii in range(0, read_len):
                    key = '%s_%s_%s' % (i, barcode, ii)
                    rc.hincrby('CELL:%s' % cell_name, key)


if __name__ == '__main__':
    command = ReadsToRedisCommand()
    command.run()
