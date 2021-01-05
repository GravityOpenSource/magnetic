import logging
from conf import conf

log_conf = conf.get('logs')

logging.basicConfig(level=log_conf.get('level', logging.INFO), filename=log_conf.get('file_path', '/var/log/tigk.log'), filemode='a')

logger = logging.getLogger(__name__)
