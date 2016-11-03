# REST API for responding to our web requests for managing the equipment
#
# GET /info/light
#   Return the current information by name ("light"). Responses:
#   {
#     "id": 2,
#     "name": "light",
#     "status": 0,
#     "status_str": "off"
#   }
#   {
#     "message": "Not found: noname"
#   }
#
# POST /update/id/2/?status=0
#   Update the status of pin #1. Responses:
#   {
#     "id": 2,
#     "name": "light",
#     "status": 0,
#     "status_str": "off"
#   }
#   {
#     "message": "Not found: ID 98643222"
#   }
#

from flask import Flask, jsonify, request
from coopcontrol import door,light

app = Flask(__name__)

def item_info(item):
    data = {
        "status":item.get_status(),
        "status_str":item.get_status_name(),
        "id":item.read_bcm_pin,
        "name":(item.__class__.__name__).lower(),
        "start":item.get_start_time().isoformat(),
        "end":item.get_end_time().isoformat()
    }
    return jsonify(data)


@app.route('/info/<name>/', methods = ['GET'])
def api_info(name):
    if name == "light":
        rs = item_info(light.Light(app.config['settings_file']))
        rs.status_code = 200
    elif name == "door":
        rs = item_info(door.Door(app.config['settings_file']))
        rs.status_code = 200
    else:
        rs = jsonify({'message':'Not found: name '+name})
        rs.status_code = 404

    return rs


@app.route('/update/id/<int:pinid>/', methods = ['POST'])
def api_update(pinid):
    status = request.form['status'] if 'status' in request.form else -1

    try:
        status = int(status)
    except ValueError as e:
        status = -1

    if not status in [0,1]:
        rs = jsonify({'message':'Invalid status'})
        rs.status_code = 400
        return rs

    l = light.Light(app.config['settings_file'])
    d = door.Door(app.config['settings_file'])

    if pinid == l.read_bcm_pin:
        l.set_status(status)
        rs = item_info(l)
    elif pinid == d.read_bcm_pin:
        d.set_status(status)
        rs = item_info(d)
    else:
        rs = jsonify({'message':'Not found: ID '+str(pinid)})
        rs.status_code = 404

    return rs


if __name__ == '__main__':
    from os import path
    parent = path.dirname(path.dirname(path.abspath('')))
    app.config['settings_file'] = path.join(parent,'data','settings.json')
    print app.config['settings_file']
    app.run(host='0.0.0.0',debug=True)