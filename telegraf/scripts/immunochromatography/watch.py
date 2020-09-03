# !/usr/bin/env python3

import sys

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

import os
import json
from common import BaseCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from daemons.prefab import run


class EventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if event.is_directory:
            return
        elif event.dest_path.endswith('.json'):
            self.analysis(event.dest_path)

    def analysis(self, path):
        with open(path, 'r', encoding='utf8') as f:
            content = f.read()
            raw_data = json.loads(content)
        res = []
        cli = command.influxdb_cli()
        for sample in raw_data.get('samples'):
            for tvalue in sample.get('tValues'):
                data = {
                    'measurement': 'immunochromatography',
                    'tags': {
                        'deviceName': raw_data.get('deviceName'),
                        'deviceID': raw_data.get('deviceID'),
                        'deviceType': raw_data.get('deviceType'),
                        'reportTime': raw_data.get('reportTime'),
                        'patientName': sample.get('patientName'),
                        'patientID': sample.get('patientID'),
                        'sampleName': sample.get('sampleName'),
                        'sampleID': sample.get('sampleID'),
                        'tID': tvalue.get('tID'),
                        'tResult': tvalue.get('tResult'),
                    },
                    'fields': {
                        'cValue': sample.get('cValue'),
                        'tValue': tvalue.get('tValue'),
                        'taxID': tvalue.get('taxID'),
                        'tName': tvalue.get('tName'),
                    }
                }
                res.append(data)
        cli.write_points(res)


class Watch(run.RunDaemon):
    def run(self):
        event_handler = EventHandler()
        observer = Observer()
        observer.schedule(event_handler, command.args.path, recursive=True)
        observer.setDaemon(False)
        observer.start()


class WatchCommand(BaseCommand):
    def parser(self):
        parser = super(WatchCommand, self).parser()
        parser.add_argument('action', choices=['start', 'stop', 'restart'])
        parser.add_argument('-p', '--path', default='immunochromatography', help='observer path')
        parser.add_argument('-P', '--pid-file', default='/tmp/immunochromatography_watch.pid', help='pid file')
        return parser

    def handle(self, args):
        args.log_file = os.path.abspath(args.log_file)
        args.pid_file = os.path.abspath(args.pid_file)
        args.path = os.path.abspath(args.path)
        watch = Watch(pidfile=args.pid_file)
        watch.args = args
        action = args.action
        watch.run()
        if action == 'start':
            watch.start()
        elif action == 'stop':
            watch.stop()
        elif action == 'restart':
            watch.restart()


if __name__ == '__main__':
    command = WatchCommand()
    command.run()
