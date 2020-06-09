#!/usr/bin/env python3

import os
from influxdb import InfluxDBClient
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse

import win32serviceutil
import win32event
import win32service


class WindowsSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "PCR Service"
    _svc_display_name_ = "PCR文件监控服务"
    _svc_description_ = "监控指定目录下的文件"

    def __init__(self, args):
        options = win32serviceutil.GetServiceCustomOption(self, 'options', '').split(',')
        self.options = {}
        for option in options:
            val = win32serviceutil.GetServiceCustomOption(self, option, '')
            self.options[option] = val
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.run = True

    def SvcDoRun(self):
        f = open(r'C:\tigk.log', 'a')
        event_handler = FastqEventHandler(self.options)
        observer = Observer()
        observer.schedule(event_handler, self.options.get('path'), recursive=True)
        observer.start()
        try:
            while self.run:
                observer.join(1)
        except Exception as e:
            f.write(str(e) + '\n')
        observer.stop()
        observer.join()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


class FastqEventHandler(FileSystemEventHandler):
    def __init__(self, options=None):
        self.influxdb_cli = InfluxDBClient(
            host=options.get('influxdb_host'),
            port=8086,
            username=options.get('influxdb_username'),
            password=options.get('influxdb_password'),
            database='telegraf',
            gzip=True
        )

    def on_created(self, event):
        f = open(r'C:\tigk.log', 'a')
        f.write(event.src_path + '\n')
        if event.is_directory:
            return
        self.insert(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self.insert(event.dest_path)

    def insert(self, path):
        cli = self.influxdb_cli
        f = open(r'C:\tigk.log', 'a')
        data = {
            'measurement': 'pcr_watch',
            'tags': {
                'dir': os.path.dirname(path)
            },
            'fields': {
                'size': os.path.getsize(path),
                'path': path
            }
        }
        try:
            cli.write_points([data])
        except Exception as e:
            f.write(str(e) + '\n')


class WatchCommand(object):
    def parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--redis-host', default='redis-server', help='redis server host')
        parser.add_argument('-i', '--influxdb-host', default='influxdb-server', help='influxdb server host')
        parser.add_argument('-iu', '--influxdb-username', default='', help='influxdb server username')
        parser.add_argument('-ip', '--influxdb-password', default='', help='influxdb server password')
        parser.add_argument('-l', '--log-file', default='C:\\tigk.log', help='log file path')
        parser.add_argument('action', choices=['install', 'start', 'stop', 'restart', 'remove'])
        parser.add_argument('-p', '--path', default='pcr', help='observer path')
        return parser

    def run(self):
        parser = self.parser()
        self.args = parser.parse_args()
        try:
            self.handle(self.args)
        except Exception as e:
            raise e

    def handle(self, args):
        args.log_file = os.path.abspath(args.log_file)
        args.path = os.path.abspath(args.path)
        win32serviceutil.HandleCommandLine(WindowsSvc)
        if args.action in ['start', 'restart']:
            options = []
            for k, v in vars(args).items():
                options.append(k)
                win32serviceutil.SetServiceCustomOption(WindowsSvc, k, v)
            win32serviceutil.SetServiceCustomOption(WindowsSvc, 'options', ','.join(options))


if __name__ == '__main__':
    command = WatchCommand()
    command.run()
