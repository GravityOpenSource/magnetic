#!/usr/bin/python3
import json
import math
import re
import sys
import os
import xmltodict
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from common import BaseCommand

from common import POSITION_STEP, LENGTH_STEP, BaseCommand


class AnalysisCommand(BaseCommand):
    def parser(self):
        parser = super(AnalysisCommand, self).parser()
        parser.add_argument('-f', '--file', help='file')
        return parser

    def handle(self, args):
        file = args.file
        root = os.path.dirname(file)
        exts = ['lamp', 'mcd', 'csv', 'xml']
        filename = os.path.splitext(os.path.basename(file))[0]
        for ext in exts:
            f = '%s.%s' % (filename, ext)
            if not os.path.exists(os.path.join(root, f)):
                print('file %s dose not exists' % f)
                exit()
        xml_file = open(os.path.join(root, '%s.xml' % filename), encoding='utf-8')
        xml_dict = xmltodict.parse(xml_file.read())
        hole_info = xml_dict['Report']['SubReport']['GroupInfoNo']['HoleInfo']
        hole_display = {}
        for hole in hole_info:
            hole_display[hole['ChipHoleNo']] = hole['HoleName']
        lamp_file = open(os.path.join(root, '%s.lamp' % filename))
        lamp_data = []
        cli = self.influxdb_cli()
        time = 1
        now = datetime.datetime.utcnow()
        for line in lamp_file.readlines()[::-1]:
            if line:
                line_list = line.strip().split('\t')
                if not self.valid_input(line_list[0]):
                    break
                for i in range(len(line_list)):
                    data = {
                        'measurement': 'pcr_data',
                        'time': now - datetime.timedelta(seconds=time * 30),
                        'tags': {
                            'sn': xml_dict['Report']['SubReport']['GroupInfoNo']['GroupInfo']['TestNo'],
                            'channel': 'channel-%s' % i,
                            'channel_display': hole_display.get(str(i + 1))
                        },
                        'fields': {
                            'second': time * 30,
                            'name': 'name-%s' % i,
                            'value': line_list[i]
                        }
                    }
                    lamp_data.append(data)
                time += 1
        try:
            cli.write_points(lamp_data)
        except Exception as e:
            print(e)

    def valid_input(self, input):
        try:
            float(input)
            return True
        except ValueError:
            return False


if __name__ == '__main__':
    command = AnalysisCommand()
    command.run()
