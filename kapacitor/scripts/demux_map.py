import os
import sys
import json

if __name__ == '__main__':
    f = open('/root/hello.txt', 'w')
    for line in sys.stdin.readlines():
        if not line:
            break
        else:
            dataset = json.loads(line).get('data').get('series')
            for data in dataset:
                for value in data.get('values'):
                    fields = dict(zip(data.get('columns'), value))
                    filename = os.path.basename(os.path.splitext(fields.get('path'))[0])
                    command = [
                        'snakemake',
                        '--snakefile /data/demux_map/Snakefile',
                        '--configfile /data/demux_map/config.yaml',
                        '--cores 8',
                        '--config',
                        'input_path=%s' % data.get('tags').get('dir'),
                        'output_path=/root',
                        'filename_stem=%s' % filename,
                        'references_file=/data/ncov2019/references.fasta'
                    ]
                    os.system(' '.join(command))
