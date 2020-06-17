import argparse
import os
import json
from flask import request
from gevent.pywsgi import WSGIServer

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
from flask import Flask
from app.tasks import print_hello, demux_map


def create_app():
    app = Flask(__name__)
    return app


app = create_app()


@app.route('/', methods=["GET"])
def index():
    cell_name = request.args.get('cell', '').strip()
    allow_restart = request.args.get('restart', '').strip() == 'true'
    return 'test'


@app.route('/tasks/demux_map', methods=['POST'])
def task_demux_map():
    data = json.loads(request.data).get('data', {}).get('series')
    if data and isinstance(data, list):
        demux_map.delay(data)
        return 'success'
    else:
        return 'fail'


def main(args):
    app.debug = args.debug == 'true'
    if app.debug:
        app.run('0.0.0.0', args.port, debug=True)
    else:
        http_server = WSGIServer(('0.0.0.0', args.port), app)
        http_server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=80, help='port')
    parser.add_argument('-d', '--debug', default='false', help='debug')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
