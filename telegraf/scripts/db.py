import redis
from influxdb import InfluxDBClient
from conf import conf


def redis_init():
    redis_conf = conf.get('redis', {})
    client = redis.Redis(
        host=redis_conf.get('host', 'redis-server'),
        port=redis_conf.get('port', 6379),
        db=redis_conf.get('database', 1),
        decode_responses=True
    )
    return client


def influxdb_init():
    influxdb_conf = conf.get('influxdb', {})
    client = InfluxDBClient(
        host=influxdb_conf.get('host', 'influxdb-server'),
        port=influxdb_conf.get('port', 8086),
        username=influxdb_conf.get('username', ''),
        password=influxdb_conf.get('password', ''),
        database=influxdb_conf.get('database', 'telegraf'),
        gzip=True
    )
    return client


influxdb_cli = influxdb_init()
redis_cli = redis_init()
