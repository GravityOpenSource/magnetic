import os
import sys
import json

if __name__ == '__main__':
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
