import json
import os
import sys
from app.celery import celery_app
from conf import conf


@celery_app.task()
def add_together(a, b):
    return a + b


@celery_app.task()
def print_hello():
    import time
    time.sleep(10)
    print('Hello World!')


@celery_app.task()
def demux_map(dataset):
    print(dataset)
    csv_reference_file = conf.get('celery').get('csv_reference_file')
    csv_output_path = conf.get('celery').get('csv_output_path')
    csv_guppy_barcoding_threads = conf.get('celery').get('csv_guppy_barcoding_threads')
    reference_file = 'reference_file=%s' % csv_reference_file
    for data in dataset:
        for value in data.get('values'):
            fields = dict(zip(data.get('columns'), value))
            filename = os.path.basename(fields.get('path'))
            os.chdir('/tmp')
            command = [
                'snakemake',
                '--snakefile /opt/scripts/demux_map/Snakefile',
                '--configfile /opt/scripts/demux_map/config.yaml',
                '--cores 2',
                '--config',
                'input_fastq=%s/%s' % (data.get('tags').get('dir'), filename),
                'output_path=%s' % os.path.join(csv_output_path, data.get('tags').get('cell')),
                reference_file,
                'guppy_barcoding_threads=%s' % csv_guppy_barcoding_threads
            ]
            if not os.system(' '.join(command)) == 0:
                sys.exit(1)
