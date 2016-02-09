# Run server through FastCGI, typically started as www-data
#

from flup.server.fcgi import WSGIServer
from inc import webservice

if __name__ == '__main__':
    WSGIServer(webservice.app, bindAddress='/tmp/coopcontrol.sock').run()
