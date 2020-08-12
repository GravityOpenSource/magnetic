import argparse
from gevent.pywsgi import WSGIServer

from app import app


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
