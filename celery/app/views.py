from . import app
import json
from flask import request
from .tasks.minknow import demux_map


@app.route('/', methods=["GET"])
def index():
    return 'test'


@app.route('/tasks/demux_map', methods=['POST'])
def task_demux_map():
    data = json.loads(request.data).get('data', {}).get('series')
    if data and isinstance(data, list):
        demux_map.delay(data)
        return 'success'
    else:
        return 'fail'
