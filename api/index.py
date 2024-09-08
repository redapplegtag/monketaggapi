import requests  # Corrected import
import random  # Corrected import
from flask import Flask, jsonify, request  # Corrected imports

app = Flask(__name__)
title = "E0744"
secret = "Z311DGCC5WONOUSF4SS6U7JXEWSAHWUIGSJKKC64FOFIT8QRRS"
auth_token = "OC|7302344786542660|dbf1874a4aa454cdd6142e59ebfd0e55"
coems = {}


def auth_header():
    return {"content-type": "application/json", "X-SecretKey": secret}


@app.route("/", methods=["POST", "GET"])
def no():
    return "yesnt"


@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfab_auth():
    getjson = request.get_json()
    required_fields = ["CustomId", "Nonce", "AppId", "Platform", "OculusId"]
    missing_fields = [field for field in required_fields if not getjson.get(field)]
    if missing_fields:
        return jsonify({"Message": "error!", "Error": "no"}), 400
    if getjson.get("AppId") != title:
        return jsonify({"Message": "skkod", "Error": "skid??"}), 400
    if not getjson.get("CustomId").startswith("OCULUS"):
        return jsonify({"Message": "scary hacker!!", "Error": "ahcker"}), 200
    if not getjson.get("Platform").startswith("Quest"):
        return jsonify({"Message": "scary hacker!!", "Error": "ahcker"}), 200

    response1 = requests.post(
        url=f'https://graph.oculus.com/user_nonce_validate?nonce={getjson["Nonce"]}&user_id={getjson["OculusId"]}&access_token={auth_token}',
        headers={"content-type": "application/json"}
    )

    if not response1.json().get("is_valid"):
        return jsonify({"Error": "no!", "Message": "no"}), 400

    url = f"https://{title}.playfabapi.com/Server/LoginWithServerCustomId"
    login_request = requests.post(
        url=url,
        json={"ServerCustomId": getjson.get("CustomId"), "CreateAccount": False},
        headers=auth_header()
    )
    if login_request.status_code == 200:
        data = login_request.json().get("data")
        ses = data.get("SessionTicket")
        token = data.get("EntityToken").get("EntityToken")
        playfab_id = data.get("PlayFabId")
        entity_type = data.get("EntityToken").get("Entity").get("Type")
        eid = data.get("EntityToken").get("Entity").get("Id")

        link_response = requests.post(
            url=f"https://{title}.playfabapi.com/Server/LinkServerCustomId",
            json={"ForceLink": True, "PlayFabId": playfab_id, "ServerCustomId": getjson.get("CustomId")},
            headers=auth_header()
        ).json()

        return jsonify({"PlayFabId": playfab_id, "SessionTicket": ses, "EntityToken": token, "EntityId": eid, "EntityType": entity_type}), 200
    else:
        return jsonify({"Message": "Login failed!", "Error": "failed"}), 400


@app.route("/api/CachePlayFabId", methods=["POST"])
def cache_playfab_id():
    getjson = request.get_json()
    coems[getjson.get("PlayFabId")] = getjson
    return jsonify({"Message": "worked1!!"}), 200

@app.route("/api/TitleData", methods=["POST", "GET"])
def get_title_data():
    response = requests.post(
        url=f"https://{title}.playfabapi.com/Server/GetTitleData",
        headers=auth_header()
    )
    if response.status_code == 200:
        return jsonify(response.json().get("data").get("Data"))
    else:
        return jsonify({}), response.status_code


@app.route("/cbfn", methods=["POST", "GET"])
def check_bad_names():
    name = request.args.get('name')
    BadNames = [
        "KKK", "PENIS", "NIGG", "NEG", "NIGA", "MONKEYSLAVE", "SLAVE", "FAG",
        "NAGGI", "TRANNY", "QUEER", "KYS", "DICK", "PUSSY", "VAGINA", "BIGBLACKCOCK",
        "DILDO", "HITLER", "KKX", "XKK", "NIGA", "NIGE", "NIG", "NI6", "PORN",
        "JEW", "JAXX", "TTTPIG", "SEX", "COCK", "CUM", "FUCK", "PENIS", "DICK",
        "ELLIOT", "JMAN", "K9", "NIGGA", "TTTPIG", "NICKER", "NICKA",
        "REEL", "NII", "@here", "!", " ", "JMAN", "PPPTIG", "CLEANINGBOT", "JANITOR", "K9",
        "H4PKY", "MOSA", "NIGGER", "NIGGA", "IHATENIGGERS", "@everyone", "TTT"
    ]
    if name not in BadNames:
        result = 0
    else:
        result = 2
    return jsonify({"Message": "the name thingy worked!", "Name": name, "Result": result})


@app.route("/GetAcceptedAgreements", methods=["POST", "GET"])
def get_auth_result():
    getjson = request.get_json()["FunctionResult"]
    return jsonify(getjson)


@app.route("/SubmitAcceptedAgreements", methods=["POST", "GET"])
def set_auth_result():
    getjson = request.get_json()["FunctionResult"]
    return jsonify(getjson)


@app.route("/GetRandomName", methods=["POST", "GET"])
def generate_random_number():
    return jsonify({"result": f"pluh!{random.randint(1000, 9999)}"})

@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_oculus_iap():
    rjson = request.get_json()

    access_token = rjson.get("userToken")
    user_id = rjson.get("userID")
    nonce = rjson.get("nonce")
    sku = rjson.get("sku")

    response = requests.post(
        url=f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"}
    )

    if response.json().get("success"):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})


@app.route("/api/photon", methods=["POST", "GET"])
def process_request():
    getjson = request.get_json()
    ticket = getjson.get("Ticket")
    nonce = getjson.get("Nonce")
    titleid = getjson.get("AppId")
    platform = getjson.get("Platform")
    user_id = getjson.get("UserId")
    appver = getjson.get("AppVersion")
    token = getjson.get("Token")
    username = getjson.get("username")

    if nonce is None:
        return jsonify({'Error': 'Bad request', 'Message': 'scaruy auther'}), 304
    if titleid != '1585E':
        return jsonify({'Error': 'Bad request', 'Message': 'Invalid titleid!'}), 403
    if platform != 'Quest':
        return jsonify({'Error': 'Bad request', 'Message': 'cheeyaj'}), 403

    return jsonify({
        "ResultCode": 1, "StatusCode": 200, "Message": "gfrthbtrhteh", "Result": 0,
        "UserId": user_id, "AppId": titleid, "AppVersion": appver, "Ticket": ticket,
        "Token": token, "Nonce": nonce, "Platform": platform, "Username": username
    }), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1421)
