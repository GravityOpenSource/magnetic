import re
import sys
import json
import math

sys.path.append('/opt/grpc')
sys.path.append('/opt/scripts')

from logs import logger
from db import redis_cli
from conf import conf


def insert_data(data):
    for item in data:
        # 合并fields与tags
        params = item.get('fields')
        params.update(item.get('tags'))
        insert_depth_data(params)
        insert_read_len_data(params)


def cell(path):
    """计算cell编号"""
    # 验证文件路径
    pattern = re.compile(r'[/\w+-]+/([\w-]+)/\w+\.csv')
    match = re.match(pattern, path)
    if not match:
        exit(200)
    return match.groups()[0]


def insert_read_len_data(item):
    """保存长度统计"""
    ont_conf = conf.get('ont')
    read_length_step = ont_conf.get('read_length_step')
    redis_key = 'CELL:READ_LEN:%(cell)s' % {'cell': cell(item.get('path'))}
    barcode = item.get('barcode')
    read_len = item.get('read_len')
    section = math.ceil(read_len / read_length_step)
    for i in range(1, section + 1):
        if i == section:
            key = '%(barcode)s_%(section)s' % {'barcode': barcode, 'section': section}
            redis_cli.hincrby(redis_key, key)
        else:
            key = '%(barcode)s_%(section)s' % {'barcode': barcode, 'section': i}
            redis_cli.hsetnx(redis_key, key, 0)


def insert_depth_data(item):
    """保存深度统计"""
    # 跳过start_coords为0的数据
    start = item.get('start_coords')
    if start == 0:
        return
    end = item.get('end_coords')
    barcode = item.get('barcode')
    ont_conf = conf.get('ont')
    depth_position_step = ont_conf.get('depth_position_step')
    read_length_step = ont_conf.get('depth_read_length_step')
    # 计算位置
    if start % depth_position_step == 0 and start != 0:
        r_start = int(start / depth_position_step) - 1
    else:
        r_start = math.floor(start / depth_position_step)
    r_end = math.ceil(end / depth_position_step)
    # 计算读长
    read_len = math.ceil(item.get('read_len') / read_length_step)
    # 保存数据
    for i in range(r_start, r_end):
        for ii in range(0, read_len):
            key = '%s_%s_%s' % (i, barcode, ii)
            redis_cli.hincrby('CELL:DEPTH:%s' % cell(item.get('path')), key)
    for i in range(1, r_end):
        for ii in range(0, read_len):
            key = '%s_%s_%s' % (i, barcode, ii)
            redis_cli.hsetnx('CELL:DEPTH:%s' % cell(item.get('path')), key, 0)


def handle():
    for line in sys.stdin.readlines():
        if not line:
            break
        else:
            try:
                insert_data(json.loads(line).get('metrics'))
            except Exception as e:
                logger.info(e)


if __name__ == '__main__':
    handle()
