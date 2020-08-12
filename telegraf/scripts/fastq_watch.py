#!/usr/bin/env python3

from common import BaseCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from daemons.prefab import run
import os


class FastqEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if event.is_directory:
            return
        elif event.dest_path.endswith('.fastq'):
            self.insert(event.dest_path)

    def get_cell_name(self, path):
        root = command.args.path.rstrip('/') + '/'
        cell_name = path.lstrip(root).split('/')[0]
        return cell_name

    def insert(self, path):
        cli = command.influxdb_cli()
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


class Watch(run.RunDaemon):
    def run(self):
        event_handler = FastqEventHandler()
        observer = Observer()
        observer.schedule(event_handler, command.args.path, recursive=True)
        observer.setDaemon(False)
        observer.start()


class FastqWatchCommand(BaseCommand):
    def parser(self):
        parser = super(FastqWatchCommand, self).parser()
        parser.add_argument('action', choices=['start', 'stop', 'restart'])
        parser.add_argument('-p', '--path', default='fastq', help='observer path')
        parser.add_argument('-P', '--pid-file', default='/tmp/fastq_watch.pid', help='pid file')
        return parser

    def handle(self, args):
        args.log_file = os.path.abspath(args.log_file)
        args.pid_file = os.path.abspath(args.pid_file)
        args.path = os.path.abspath(args.path)
        watch = Watch(pidfile=args.pid_file)
        watch.args = args
        action = args.action
        if action == 'start':
            watch.start()
        elif action == 'stop':
            watch.stop()
        elif action == 'restart':
            watch.restart()


if __name__ == '__main__':
    command = FastqWatchCommand()
    command.run()
