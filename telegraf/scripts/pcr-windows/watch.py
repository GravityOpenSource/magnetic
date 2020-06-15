import os
from influxdb import InfluxDBClient
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
import datetime
import time
import xmltodict
import zipfile

import win32serviceutil
import win32event
import win32service
import logging


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
        self.logger = logging.getLogger(__name__)
        fh = logging.FileHandler(filename=self.options.get('log_file'), mode='a', encoding='utf-8')
        logging.basicConfig(handlers=[fh], level=logging.INFO)

    def SvcDoRun(self):
        pcr_event_handler = PCREventHandler(self)
        rdml_event_handler = RDMLEventHandler(self)
        observer = Observer()
        observer.schedule(pcr_event_handler, self.options.get('path'), recursive=True)
        observer.schedule(rdml_event_handler, self.options.get('rdml_path'), recursive=True)
        observer.start()
        try:
            while self.run and observer.is_alive():
                observer.join(1)
        except Exception as e:
            self.logger.error(str(e))
        observer.stop()
        observer.join()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


class PCREventHandler(FileSystemEventHandler):
    def __init__(self, svc: WindowsSvc):
        self.influxdb_cli = InfluxDBClient(
            host=svc.options.get('influxdb_host'),
            port=8086,
            username=svc.options.get('influxdb_username'),
            password=svc.options.get('influxdb_password'),
            database='telegraf',
            gzip=True
        )
        self.logger = svc.logger

    def on_any_event(self, event):
        self.logger.info('PCR-' + event.event_type + ':' + event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        try:
            self.insert(event.src_path)
            self.analysis(event.src_path)
        except Exception as e:
            self.logger.error(str(e))

    # def on_moved(self, event):
    #     if event.is_directory:
    #         return
    #     self.insert(event.dest_path)
    #     self.analysis(event.dest_path)

    # def on_modified(self, event):
    #     # if event.is_directory:
    #         return
    #     self.insert(event.src_path)
    #     self.analysis(event.src_path)

    def insert(self, path):
        cli = self.influxdb_cli
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
            self.logger.error(str(e))

    def analysis(self, path):
        root = os.path.dirname(path)
        exts = ['lamp', 'mcd', 'csv', 'xml']
        filename = os.path.splitext(os.path.basename(path))[0]
        for ext in exts:
            f = '%s.%s' % (filename, ext)
            if not os.path.exists(os.path.join(root, f)):
                return
        xml_file = open(os.path.join(root, '%s.xml' % filename), encoding='utf-8')
        xml_dict = xmltodict.parse(xml_file.read())
        hole_info = xml_dict['Report']['SubReport']['GroupInfoNo']['HoleInfo']
        hole_display = {}
        for hole in hole_info:
            hole_display[hole['ChipHoleNo']] = hole['HoleName']
        lamp_file = open(os.path.join(root, '%s.lamp' % filename))
        lamp_data = []
        cli = self.influxdb_cli
        time = 1
        lamp_content = lamp_file.readlines()
        start_time = datetime.datetime.strptime(lamp_content[1].split('\t')[3], '%Y-%m-%d %X')
        utc_time = self.local2utc(start_time)
        for line in lamp_content[::-1]:
            if line:
                line_list = line.strip().split('\t')
                if not self.valid_input(line_list[0]):
                    break
                for i in range(len(line_list)):
                    data = {
                        'measurement': 'pcr_data',
                        'time': utc_time - datetime.timedelta(seconds=time * 30),
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
            self.logger.error(str(e))

    def valid_input(self, input):
        try:
            float(input)
            return True
        except ValueError:
            return False

    def local2utc(self, local_st):
        time_struct = time.mktime(local_st.timetuple())
        utc_st = datetime.datetime.utcfromtimestamp(time_struct)
        return utc_st


class RDMLEventHandler(FileSystemEventHandler):
    def __init__(self, svc: WindowsSvc):
        self.influxdb_cli = InfluxDBClient(
            host=svc.options.get('influxdb_host'),
            port=8086,
            username=svc.options.get('influxdb_username'),
            password=svc.options.get('influxdb_password'),
            database='telegraf',
            gzip=True
        )
        self.logger = svc.logger

    def on_any_event(self, event):
        self.logger.info('RDML-' + event.event_type + ':' + event.src_path)

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('rdml'):
            return
        try:
            self.analysis(event.src_path)
        except Exception as e:
            self.logger.error(str(e))

    def analysis(self, path):
        z = zipfile.ZipFile(path, 'r')
        for f in z.namelist():
            xml_file = z.read(f)
            xml_dict = xmltodict.parse(xml_file)
            cq_data = []
            for item in xml_dict['rdml']['experiment']['run']['react']:
                adp_data = []
                mdp_data = []
                cq_data.append({
                    'measurement': 'pcr_rdml_cq',
                    'tags': {
                        'sample': item['sample']['@id'],
                        'tar': item['data']['tar']['@id'],
                        'ID': '%03d' % int(item['@id']),
                        'excl': item['data'].get('excl', 'FALSE')
                    },
                    'fields': {
                        'value': item['data']['cq']
                    }
                })
                for adp in item['data']['adp']:
                    data = {
                        'measurement': 'pcr_rdml_adp',
                        'tags': {
                            'sample': item['sample']['@id'],
                            'tar': item['data']['tar']['@id'],
                            'cyc': adp['cyc'],
                        },
                        'fields': {
                            'fluor': adp['fluor']
                        }
                    }
                    adp_data.append(data)
                for mdp in item['data']['mdp']:
                    data = {
                        'measurement': 'pcr_rdml_mdp',
                        'tags': {
                            'sample': item['sample']['@id'],
                            'tar': item['data']['tar']['@id'],
                            'tmp': mdp['tmp'],
                        },
                        'fields': {
                            'fluor': mdp['fluor']
                        }
                    }
                    mdp_data.append(data)
                try:
                    self.influxdb_cli.write_points(adp_data)
                    self.influxdb_cli.write_points(mdp_data)
                except Exception as e:
                    self.logger.error(str(e))
            try:
                self.influxdb_cli.write_points(cq_data)
            except Exception as e:
                self.logger.error(str(e))


class WatchCommand(object):
    def parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('action', choices=['install', 'start', 'stop', 'restart', 'remove'])
        parser.add_argument('-i', '--influxdb-host', default='influxdb-server', help='influxdb server host')
        parser.add_argument('-iu', '--influxdb-username', default='', help='influxdb server username')
        parser.add_argument('-ip', '--influxdb-password', default='', help='influxdb server password')
        parser.add_argument('-l', '--log-file', default='C:/ProgramData/Telegraf/watch.log', help='log file path')
        parser.add_argument('-p', '--path', default='pcr', help='pcr observer path')
        parser.add_argument('-rp', '--rdml-path', default='rdml', help='rdml observer path')
        return parser

    def run(self):
        parser = self.parser()
        args = parser.parse_args()
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
