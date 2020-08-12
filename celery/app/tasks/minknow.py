from app.celery import celery_app
import os
import json
import sys

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
    for data in dataset:
        for value in data.get('values'):
            fields = dict(zip(data.get('columns'), value))
            filename = os.path.basename(os.path.splitext(fields.get('path'))[0])
            os.chdir('/tmp')
            command = [
                'snakemake',
                '--snakefile /opt/scripts/demux_map/Snakefile',
                '--configfile /opt/scripts/demux_map/config.yaml',
                '--cores 8',
                '--config',
                'input_path=%s' % data.get('tags').get('dir'),
                'output_path=/data/rampart_annotations/%s' % data.get('tags').get('cell'),
                'filename_stem=%s' % filename,
                'references_file=/data/ncov2019/references.fasta'
            ]
            if not os.system(' '.join(command)) == 0:
                sys.exit(1)