import logging
import argparse
import redis
import platform
from influxdb import InfluxDBClient
from logs import logger
from db import redis_cli, influxdb_cli

POSITION_STEP = 300  # 位点区间长度
LENGTH_STEP = 500  # reads长度区间长度


class BaseCommand:
    def __init__(self):
        self._args = None
        self._logger = None

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        if not self._args:
            self._args = args

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        if not self._logger:
            self._logger = logger

    def run(self):
        parser = self.parser()
        self.args = parser.parse_args()
        self.logger = self._init_logger()
        try:
            self.handle(self.args)
        except Exception as e:
            self.logger.error(e)
            raise e

    def handle(self, args):
        """

        :param args:
        :return:
        """
        pass

    def _init_logger(self):
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, filename=self.args.log_file, filemode='a')
        return logger

    def parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--redis-host', default='redis-server', help='redis server host')
        parser.add_argument('-i', '--influxdb-host', default='influxdb-server', help='influxdb server host')
        parser.add_argument('-iu', '--influxdb-username', default='', help='influxdb server username')
        parser.add_argument('-ip', '--influxdb-password', default='', help='influxdb server password')
        parser.add_argument('-l', '--log-file', default='/var/log/tigk.log', help='log file path')
        return parser

    def redis_cli(self):
        client = redis.Redis(host=self.args.redis_host, port=6379, db=1, decode_responses=True)
        return client

    def influxdb_cli(self):
        client = InfluxDBClient(
            host=self.args.influxdb_host,
            port=8086,
            username=self.args.influxdb_username,
            password=self.args.influxdb_password,
            database='telegraf',
            gzip=True
        )
        return client


class BasicCommand:
    def run(self):
        parser = self.parser()
        self.args = parser.parse_args()
        self.logger = logger
        try:
            self.handle(self.args)
        except Exception as e:
            self.logger.error(e)
            raise e

    def handle(self, args):
        """

        :param args:
        :return:
        """
        pass

    def parser(self):
        parser = argparse.ArgumentParser()
        return parser

    def redis_cli(self):
        return redis_cli

    def influxdb_cli(self):
        return influxdb_cli