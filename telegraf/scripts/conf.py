import yaml
from pathlib import Path

conf_dir = Path('/etc/tigk_conf')

conf_file = conf_dir / 'tigk.yaml'

with open(str(conf_file)) as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)

# samples conf
samples_conf_dir = conf_dir / 'samples'
