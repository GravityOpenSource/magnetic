#!/usr/bin/python3
from common import BaseCommand
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from daemons.prefab import run
import os


class FastqEventHandler(FileSystemEventHandler):
    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        elif event.src_path.endswith('.fastq'):
            self.insert(event)

    def on_moved(self, event):
        command.logger.info('hello moved')

    def get_cell_name(self, src_path):
        root = command.args.path.rstrip('/') + '/'
        cell_name = src_path.lstrip(root).split('/')[0]
        return cell_name

    def insert(self, event):
        cli = command.influxdb_cli()
        src_path = event.src_path
        data = {
            'measurement': 'p48_fastq',
            'tags': {
                'cell': self.get_cell_name(src_path),
                'dir': os.path.dirname(src_path)
            },
            'fields': {
                'size': os.path.getsize(src_path),
                'path': src_path
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
