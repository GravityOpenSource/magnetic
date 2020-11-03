import sys

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

import os
from common import BasicCommand
from conf import conf
from db import influxdb_cli
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ont_conf = conf.get('ont')
watch_path = ont_conf.get('fastq_watch_path')


class FastqEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if event.is_directory:
            return
        elif event.dest_path.endswith('.fastq'):
            self.insert(event.dest_path)

    def get_cell_name(self, path):
        root = watch_path.rstrip('/') + '/'
        cell_name = path[len(root) + 1:].split('/')[0]
        return cell_name

    def insert(self, path):
        cli = influxdb_cli
        data = {
            'measurement': 'fastq_watch',
            'tags': {
                'cell': self.get_cell_name(path),
                'dir': os.path.dirname(path)
            },
            'fields': {
                'size': os.path.getsize(path),
                'path': path
            }
        }
        cli.write_points([data])


class FastqWatchCommand(BasicCommand):
    def handle(self, args):
        event_handler = FastqEventHandler()
        observer = Observer()
        observer.schedule(event_handler, watch_path, recursive=True)
        observer.setDaemon(False)
        observer.start()


if __name__ == '__main__':
    command = FastqWatchCommand()
    command.run()
