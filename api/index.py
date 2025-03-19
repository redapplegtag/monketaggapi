import flask
from flask import Flask, requests, jsonify

app = Flask(__name__)

baddestnamesever = [
    "NIGGA", "NIGGER", "NIGA", "BLACKNIG", "NIG", "IHATENIG", "NIGGYWIGGY",
    "NIGGLER", "NIGGLA", "HITLER", "ADOLFHITLER", "IHATEJEWS", "SLAVE",
    "SLAVEOWNER", "NAZI", "NAZ1", "N1993R", "NIGGAMAN", "gorillaNIG",
    "FUCKBLACK", "GEORGEFL", "GEORGFL", "KKK", "FAGGOT", "FAG", 
    "KKKMEMBER", "KKKLEADER", "FAGGYWAGGY", "XXX" "3KS", "PORN", 
    "CHILDPORN", "P0RN", "CH1LDP0RN", "JERKMATE", "J3RKMATE", "KKKMAN" # u can add more lol
]

@app.route("/", methods=["POST", "GET"])
def hub():
    return "forced to do this stupid ass thing but works ig idk"

@app.route("/api/checkforbadname", methods=["POST"])
def start():
    name = requests.get_json().get("FunctionArgument", {}).get("name")
    room = requests.get_json().get("FunctionArgument", {}).get("forRoom")

    if name in baddestnamesever():
        return jsonify ({
            "result": 2
        }), 200
    else:
        return jsonify({
            "result": 0
        })

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
