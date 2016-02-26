# Run server through FastCGI, typically started as www-data
#

from flup.server.fcgi import WSGIServer
import sys, logging
import equip_json

if len(sys.argv) > 1:
    settings = sys.argv[1]
else:
    logging.warning("Settings file location is required as an argument")
    sys.exit(1)

if __name__ == '__main__':
    # set this if you like to see more error info during debugging
    # equip_json.app.config['DEBUG'] = True

    equip_json.app.config['settings_file'] = settings
    WSGIServer(equip_json.app, bindAddress='/tmp/coopcontrol.sock').run()
