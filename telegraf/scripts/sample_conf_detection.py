import os
import yaml
from conf import samples_conf_dir
from logs import logger
from db import influxdb_cli


def insert_sample(sample_name):
    measurement = 'sample_info'
    sql = 'show tag values from sample_info with key = "sample_name" where sample_name = \'%(sample_name)s\'' % {'sample_name': sample_name}
    if len(list(influxdb_cli.query(sql).get_points())) > 0:
        return
    data = '%s,%s value=true' % (
        measurement,
        'sample_name=%s' % sample_name
    )
    influxdb_cli.write_points(points=[data], protocol='line')


def insert_data(data, data_type):
    insert_sample(data.get('sample_name'))
    measurement = 'sample_info_%s' % data_type
    sql = 'show tag values from %(measurement)s with key = "sample_name" where sample_name = \'%(sample_name)s\'' % {'measurement': measurement,
                                                                                                                     'sample_name': data.get('sample_name')}
    if len(list(influxdb_cli.query(sql).get_points())) > 0:
        return
    data = '%s,%s value=true' % (
        measurement,
        ','.join(['%s=%s' % (k, v) for k, v in data.items()]),
    )
    influxdb_cli.write_points(points=[data], protocol='line')


def sync_samples(sample_conf):
    for sample in sample_conf:
        ont_result(sample)
        pcr_result(sample)
        immunochromatography_result(sample)


def ont_result(sample):
    cell = sample.get('ont', {}).get('cell')
    barcode = sample.get('ont', {}).get('barcode')
    if not cell or not barcode:
        return
    sql = 'show tag values from reads_length_stats with key = "cell" where cell = \'%(cell)s\'' % {'cell': cell}
    cell_set = influxdb_cli.query(sql)
    if len(list(cell_set.get_points())) > 0:
        sql = 'show tag values from reads_length_stats with key = "barcode" where cell = \'%(cell)s\' and barcode = \'%(barcode)s\'' % {'cell': cell, 'barcode': barcode}
        barcode_set = influxdb_cli.query(sql)
        if len(list(barcode_set.get_points())) > 0:
            insert_data({'sample_name': sample.get('name'), 'cell': cell, 'barcode': barcode}, 'ont')


def pcr_result(sample):
    sn = sample.get('pcr', {}).get('sn')
    run_well = sample.get('pcr', {}).get('run_well', {}).get('main')
    if not sn or not run_well:
        return
    sql = 'show tag values from pcr_rdml_adp with key = "sample" where sample = \'%(run_well)s\'' % {'run_well': run_well}
    run_well_set = influxdb_cli.query(sql)
    if len(list(run_well_set.get_points())) > 0:
        insert_data({
            'sample_name': sample.get('name'),
            'sn': sn,
            'run_well': run_well,
            'positive_control': sample.get('pcr', {}).get('run_well', {}).get('positive_control', ''),
            'negative_control': sample.get('pcr', {}).get('run_well', {}).get('negative_control', '')
        }, 'pcr')


def immunochromatography_result(sample):
    sample_id = sample.get('immunochromatography', {}).get('sample_id')
    report_time = sample.get('immunochromatography', {}).get('report_time')
    if not sample_id or not report_time:
        return
    sql = 'show tag values from immunochromatography with key = "sampleID" where sampleID = \'%(sample_id)s\' and reportTime = \'%(report_time)s\'' % {'sample_id': sample_id,
                                                                                                                                                       'report_time': report_time}
    sample_set = influxdb_cli.query(sql)
    if len(list(sample_set.get_points())) > 0:
        insert_data({'sample_name': sample.get('name'), 'sample_id': sample_id, 'report_time': report_time}, 'immunochromatography')


if __name__ == '__main__':
    conf_files = os.listdir(str(samples_conf_dir))
    for conf_file in conf_files:
        with open(str(samples_conf_dir / conf_file)) as f:
            sample_conf = yaml.load(f, Loader=yaml.FullLoader)
            sync_samples(sample_conf.get('samples'))
