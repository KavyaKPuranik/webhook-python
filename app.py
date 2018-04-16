# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import datetime
import json
import os
import re

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
	
	
    baseurl = "ttps://api.railwayapi.com/v2/"
    apikey = "/apikey/3gleroll53"
	
	
    print("Request:")
    print(json.dumps(req, indent=4))
	
	# Call Functions based on action
    if req.get("result").get("action") == "trainStatus":
        res = processStatus(req)
    if req.get("result").get("action") == "trainRoute":
        res = processRoute(req)
    if req.get("result").get("action") == "stationCode":
        res = processCode(req)
    if req.get("result").get("action") == "Tr_Name_to_Code":
        res = processTrainNumber(req)
		
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

# ----------------------------------------------------------------------------------------------------------
# Station Code
# ----------------------------------------------------------------------------------------------------------
def processCode(req):
    if req.get("result").get("action") != "stationCode":
        return {}
    baseurl = "https://api.railwayapi.com/v2/suggest-station/name/"
    remain = "/apikey/3gleroll53"
    yql_query = makeQueryTrain(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultCodeTrain(data)
    return res
def processCode(req):
    if req.get("result").get("action") != "stationCode":
        return {}
    baseurl = "https://api.railwayapi.com/v2/suggest-station/name/"
    remain = "/apikey/3gleroll53"
    yql_query = makeQueryForPlace(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultCodePlace(data)
    return res

def makeQueryTrain(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainnum = parameters.get("Train")
    if trainnum is None:
        return None
    return trainnum
def makeQueryForPlace(req):
    result = req.get("result")
    parameters = result.get("parameters")
    trainnum = parameters.get("geo-city")
    if trainnum:
        return trainnum
    trainnum2 = parameters.get("place") 
    if trainnum2:
        return trainnum2
    return {}
		
def makeWebhookResultCodeTrain(data):
    speech = ""
    for routes in data['route']:
        speech =  speech +routes['station']['name'] + " -> "
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }
def makeWebhookResultCodePlace(data):
    msg = []
    speech = ""
    for station in data['stations']:
        speech = speech + station['name'] +"  -  "+ station['code'] + ", "
        msg.append(station['name'] +"  -  "+ station['code'])
    messages = [{"type": 0, "speech": s[0]} for s in zip(msg)]
    reply = {
            "speech": speech,
            "displayText": speech,
            "messages": messages,
            "source": "webhook-dm"
            }
    return reply


# ----------------------------------------------------------------------------------------------------------
# Train Route
# ----------------------------------------------------------------------------------------------------------
def processRoute(req):
    if req.get("result").get("action") != "trainRoute":
        return {}
    baseurl = "https://api.railwayapi.com/v2/route/train/"
    remain = "/apikey/3gleroll53"
    yql_query = makeQueryTrain(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultRoute(data)
    return res
	
def makeWebhookResultRoute(data):
    speech = ""
    for routes in data['route']:
        speech =  speech +routes['station']['name'] + " -> "
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }


# ----------------------------------------------------------------------------------------------------------
# Train Status
# ----------------------------------------------------------------------------------------------------------
def processStatus(req):
    if req.get("result").get("action") != "trainStatus":
        return {}
    baseurl = "https://api.railwayapi.com/v2/live/train/" 
    i = datetime.datetime.now()
    day = i.day 
    month = i.month 
    year = i.year
    today = "10-04-2018"
    remain = "/date/"+today+"/apikey/3gleroll53/"
    yql_query = makeQueryTrain(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + remain
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResultStatus(data)
    return res

def makeWebhookResultStatus(data):
    speech = data.get('position')
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "webhook-dm"
    }

	


# ----------------------------------------------------------------------------------------------------------
# Connection
# ----------------------------------------------------------------------------------------------------------	
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
