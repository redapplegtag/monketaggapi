# this isn't really a leak i guess because cycy said i can post this on gangalangshlawgitty
import requests
import random
from flask import Flask, jsonify, request


class GameInfo():

    def __init__(self):
        self.TitleId: str = "C11BB"
        self.SecretKey: str = "DAK4NZC1WK6HKNKSF1PJOGWJJHHOBRG1QQR6UBPNOC1X9R53TY"
        self.ApiKey: str = "OC|7302344786542660|dbf1874a4aa454cdd6142e59ebfd0e55"

    def GetAuthHeaders(self) -> dict:
        return {
            "content-type": "application/json",
            "X-SecretKey": self.SecretKey
        }

    def GetTitle(self) -> str:
        return self.TitleId


settings: GameInfo = GameInfo()
app: Flask = Flask(__name__)
playfabCache: dict = {}
muteCache: dict = {}

settings.TitleId = "C11BB"
settings.SecretKey = "DAK4NZC1WK6HKNKSF1PJOGWJJHHOBRG1QQR6UBPNOC1X9R53TY"
settings.ApiKey = "OC|7302344786542660|dbf1874a4aa454cdd6142e59ebfd0e55"


def ReturnFunctionJson(data, funcname, funcparam={}):
    rjson = data["FunctionParameter"]

    userId: str = rjson.get("CallerEntityProfile").get("Lineage").get(
        "TitlePlayerAccountId")

    req = requests.post(
        url=
        f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers=settings.GetAuthHeaders())

    if req.status_code == 200:
        return jsonify(
            req.json().get("data").get("FunctionResult")), req.status_code
    else:
        return jsonify({}), req.status_code


def GetIsNonceValid(nonce: str, oculusId: str):
    req = requests.post(
        url=f'https://graph.oculus.com/user_nonce_validate?nonce=' + nonce +
        '&user_id=' + oculusId + '&access_token=' + settings.ApiKey,
        headers={"content-type": "application/json"})
    return req.json().get("is_valid")


@app.route("/", methods=["POST", "GET"])
def main():
    return "Made By cycy"

#replace https://auth-prod.gtag-cf.com/api/PlayFabAuthentication with this endpoint
@app.route('/api/PlayFabAuthentication', methods=['POST'])
def playfabauth():
    data = request.json
    if data is not None and 'CustomId' not in data:
        return jsonify({
            'Error': 'Bad Request',
            'Message': 'CustomId is required'
        }), 400
    custom_id = data['CustomId']
    numbers = custom_id.split("OCULUS")[1]
    new_id = f"OCULUS{numbers}"
    headers = {'Content-Type': 'application/json', 'X-SecretKey': SecretKey}

    # PlayFab login
    login_endpoint = f"https://{settings.TitleId}.playfabapi.com/Client/LoginWithCustomId"
    login_payload = {
        'TitleId': TitleId,
        'CustomId': new_id,
        'CreateAccount': True
    }
    login_response = requests.post(login_endpoint,
                                   headers=headers,
                                   json=login_payload)
    if login_response.status_code == 200:
        send_to_discord("Playfab auth was triggered logged in sucessfully")
        response_data = login_response.json()["data"]
        playfab_id = response_data['PlayFabId']
        session_ticket = response_data['SessionTicket']

        # For user authentication, use SessionTicket
        user_auth_headers = {
            'Content-Type': 'application/json',
            'X-Authorization': session_ticket
        }
        link_endpoint = f"https://{settings.TitleId}.playfabapi.com/Client/LinkCustomID"
        link_payload = {
            'PlayFabId': old_id,
            'CustomId': new_id,
            'ForceLink': True
        }
        link_response = requests.post(link_endpoint,
                                      headers=user_auth_headers,
                                      json=link_payload)
        if link_response.status_code == 200:
            send_to_discord(
                "Playfab auth was triggered linked account sucessfully")
            print("CustomID successfully linked to the PlayFab account.")
        else:
            print(
                f"Failed to link CustomID: {link_response.status_code} - {link_response.text}"
            )

        entityId = response_data['EntityToken']['Entity']['Id']
        entityType = response_data['EntityToken']['Entity']['Type']
        entityToken = response_data['EntityToken']['EntityToken']
        return jsonify({
            'SessionTicket': session_ticket,
            'PlayFabId': playfab_id,
            'EntityId': entityId,
            'EntityType': entityType,
            'EntityToken': entityToken
        }), 200

    elif login_response.status_code == 403:
        ban_info = login_response.json()
        if ban_info.get('errorCode') == 1002:
            ban_message = ban_info.get('errorMessage',
                                       "No ban message provided.")
            ban_details = ban_info.get('errorDetails', {})
            ban_expiration_key = next(iter(ban_details.keys()), None)
            ban_expiration_list = ban_details.get(ban_expiration_key, [])
            ban_expiration = ban_expiration_list[0] if len(
                ban_expiration_list) > 0 else "No expiration date provided."
            print(ban_info)
            return jsonify({
                'BanMessage': ban_expiration_key,
                'BanExpirationTime': ban_expiration
            }), 403
        else:
            error_message = ban_info.get('errorMessage',
                                         'Forbidden without ban information.')
            return jsonify({
                'Error': 'PlayFab Error',
                'Message': error_message
            }), 403

    else:
        print(f'Login Response: {login_response.json()}')

        playfab_error = login_response.json().get("error", {})
        return jsonify({
            'Error': 'PlayFab Error',
            'Message': 'Login Failed',
            'PlayFabError': playfab_error
        }), login_response.status_code


#replace https://auth-prod.gtag-cf.com/api/CachePlayFabId with this endpoint
@app.route("/api/CachePlayFabId", methods=["POST"])
def cacheplatfabid():
    rjson = request.get_json()

    playfabCache[rjson.get("PlayFabId")] = rjson

    return jsonify({"Message": "Success"}), 200


#replace https://title-data.gtag-cf.com with this endpoint
@app.route("/api/titledata", methods=["POST", "GET"])
def titledata():

    req = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.GetAuthHeaders())

    if req.status_code == 200:
        return jsonify(req.json().get("data").get("Data"))
    else:
        return jsonify({})

@app.route("/api/CheckForBadName", methods=["POST"])
def checkforbadname():
    rjson = request.get_json().get("FunctionResult")

    name: str = rjson.get("name").upper()

    if ["NIGGER", "NIGGA", "FAGGOT", "NIGG", "NIGGAR"].__contains__(name):
        return jsonify({"result": 2})
    else:
        return jsonify({"result": 0})


@app.route("/api/GetAcceptedAgreements", methods=["POST"])
def getacceptedagreements():
    rjson = request.get_json()["FunctionResult"]

    return jsonify(rjson)


@app.route("/api/SubmitAcceptedAgreements", methods=["POST"])
def submitacceptedagreements():
    rjson = request.get_json()["FunctionResult"]

    return jsonify(rjson)


@app.route("/api/GetRandomName", methods=["POST", "GET"])
def GetRandomName():
    return jsonify({"result": "gorilla" + random.randint(1000, 9999)})


# replace https://iap.gtag-cf.com/api/ConsumeOculusIAP with this endpoint
@app.route("/api/consumeoculusiap", methods=["POST"])
def consumeoculusiap():
    rjson = request.get_json()

    accessToken = rjson.get("userToken")
    userId = rjson.get("userID")
    playFabId = rjson.get("playFabId")
    nonce = rjson.get("nonce")
    platform = rjson.get("platform")
    sku = rjson.get("sku")
    debugParams = rjson.get("debugParemeters")

    req = requests.post(
        url=
        f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={userId}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"})

    if bool(req.json().get("success")):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})


@app.route("/api/ReturnMyOculusHashV2")
def returnmyoculushashv2():
    return ReturnFunctionJson(request.get_json(), "ReturnMyOculusHash")


@app.route("/api/ReturnCurrentVersionV2", methods=["POST", "GET"])
def returncurrentversionv2():
    return ReturnFunctionJson(request.get_json(), "ReturnCurrentVersion")


@app.route("/api/TryDistributeCurrencyV2", methods=["POST", "GET"])
def trydistributecurrencyv2():
    return ReturnFunctionJson(request.get_json(), "TryDistributeCurrency")


@app.route("/api/BroadCastMyRoomV2", methods=["POST", "GET"])
def broadcastmyroomv2():
    return ReturnFunctionJson(request.get_json(), "BroadCastMyRoom",
                              request.get_json()["FunctionParameter"])


@app.route("/api/ShouldUserAutomutePlayer", methods=["POST", "GET"])
def shoulduserautomuteplayer():
    return jsonify(muteCache)


@app.route("/api/photon/authenticate", methods=["POST"])
def photonauthenticate():
    if request.method.upper() == "GET":
        userId = request.args.get("username")
        token = request.args.get("token")

        req = requests.post(
            url=
            f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers=settings.GetAuthHeaders())

        if req.status_code == 200:
            nickName: str = req.json().get("UserInfo").get(
                "UserAccountInfo").get("Username")
            if nickName == "" or nickName is None:
                nickName = ""  
            return jsonify({
                'resultCode': 1,
                'message':
                'Authenticated user',
                'nickname': nickName
            })

        else:
            if userId is None or (userId is not None and len(userId) != 16):
                return jsonify({
                    'resultCode': 2,
                    'message': 'Invalid token',
                    'userId': None,
                    'nickname': None
                })
            elif token is None:
                return jsonify({
                    'resultCode': 3,
                    'message': 'Failed to parse token from request',
                    'userId': None,
                    'nickname': None
                })
            else:
                return jsonify({
                    'resultCode': 0,
                    'message': "Something went wrong",
                    'userId': None,
                    'nickname': None
                })
    elif request.method.upper() == "POST":

        authPostData: dict = request.get_json()

        userId = request.args.get("username")
        token = request.args.get("token")

        req = requests.post(
            url=
            f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers=settings.GetAuthHeaders())

        if req.status_code == 200:
            nickName: str = req.json().get("UserInfo").get(
                "UserAccountInfo").get("Username")
            nickName = "" if nickName == "" or nickName is None else nickName
                

            return jsonify({
                'resultCode': 1,
                'message':
                'Authenticated user',
                'nickname': nickName
            })

        else:
            if userId is None or (userId is not None and len(userId) != 16):
                return jsonify({
                    'resultCode': 2,
                    'message': 'Invalid token',
                    'userId': None,
                    'nickname': None
                })
            elif token is None:
                return jsonify({
                    'resultCode': 3,
                    'message': 'Failed to parse token from request',
                    'userId': None,
                    'nickname': None
                })
            else:
                successJson: dict = {
                    'resultCode': 0,
                    'message': "Something went wrong",
                    'userId': None,
                    'nickname': None
                }

                for key, value in authPostData.items():
                    successJson[key] = value

                return jsonify(successJson)

    else:
        return jsonify({
            "Message":
            "Use a POST or GET Method instead of " + request.method.upper()
        })


if __name__ == "__main__":

    app.run("0.0.0.0", 8080)
