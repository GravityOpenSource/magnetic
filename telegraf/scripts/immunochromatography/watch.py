import sys

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

import json
from common import BasicCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from conf import conf
from db import influxdb_cli
from logs import logger

immunochromatography_conf = conf.get('immunochromatography')
watch_path = immunochromatography_conf.get('watch_path')


class EventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        logger.info(event)
        if event.is_directory:
            return
        elif event.dest_path.endswith('.json'):
            self.analysis(event.dest_path)

    def analysis(self, path):
        with open(path, 'r', encoding='utf8') as f:
            content = f.read()
            raw_data = json.loads(content)
        res = []
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
        influxdb_cli.write_points(res)


class WatchCommand(BasicCommand):
    def handle(self, args):
        event_handler = EventHandler()
        observer = Observer()
        observer.schedule(event_handler, watch_path, recursive=True)
        observer.setDaemon(False)
        observer.start()


if __name__ == '__main__':
    command = WatchCommand()
    command.run()
