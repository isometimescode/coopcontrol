# REST API for responding to our web requests
#
# GET /info/2
# GET /info/light
#   Return the current information for either the pin ("2") or by name ("light"). Responses:
#   {
#     "id": 2,
#     "name": "light",
#     "status": 0,
#     "status_str": "off"
#   }
#   {'message':'Not found: ID 5/name '}
#
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
import sys
import lightmod, doormod

app = Flask(__name__)

def light_info():
    o = lightmod.Light()
    data = {
        "status":(1 if o.getlight() == o.on else 0),
        "status_str":("on" if o.getlight() == o.on else "off"),
        "id":lightmod.coop_settings.pin_lights,
        "name":"light"
    }
    return jsonify(data)

def door_info():
    o = doormod.Door()
    data = {
        "status":o.getdoor(),
        "status_str":("open" if o.getdoor() == 1 else "closed"),
        "id":doormod.coop_settings.pin_door,
        "name":"door"
    }
    return jsonify(data)

@app.route('/info/<int:pinid>/', methods = ['GET'])
@app.route('/info/<name>/', methods = ['GET'])
def api_info(pinid = -1, name = ""):
    if (pinid >= 0 and pinid == lightmod.coop_settings.pin_lights) or name == "light":
        rs = light_info()
        rs.status_code = 200
    elif (pinid >= 0 and pinid == doormod.coop_settings.pin_door) or name == "door":
        rs = door_info()
        rs.status_code = 200
    else:
        rs = jsonify({'message':'Not found: ID '+str(pinid)+'/name '+name})
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

    if pinid == lightmod.coop_settings.pin_lights:
        o = lightmod.Light()
        o.changelight(o.on) if status == 1 else o.changelight(o.off)
        rs = light_info()
    elif pinid == doormod.coop_settings.pin_door:
        o = doormod.Door()
        if o.getdoor() != status:
            o.changedoor(status)
        rs = door_info()
    else:
        rs = jsonify({'message':'Not found: ID '+str(pinid)})
        rs.status_code = 404

    return rs

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)