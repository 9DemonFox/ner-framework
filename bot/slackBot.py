from urllib import request, parse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import os
import sys
from urllib.parse import *
sys.path.append('../')
from framework.model.extractmodel import ExtractionModel
from pprint import pprint

'''
{
    "channel": "C1H9RESGL",
    "text": "Text here for notifications",
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
			}
		}
	]
}
'''

#########global model_name
###global model_group

#model_name = "movie3"
#model_group = "movie"
#model = ExtractionModel("movie", "movie3")



def createBlockMessage(str):
    subDict = {}
    subDict["type"] = "mrkdwn"
    subDict["text"] = str

    dict = {}
    dict["type"] = "section"
    dict["text"] = subDict

    response = {}
    arr = []
    arr.append(dict)
    response["channel"] = "#random"
    response["text"] = "ACK"
    response["blocks"] = arr
    response["status"] = 200
    response["ok"]= "true"

    return response


def createModelList(models):
    outer = {}
    inner_blocks = []

    sendMessage(createBlockMessage("*Generating list of of models...*"))

    for model in models:
        trained_models = os.listdir("../framework/model/models/" + model)
        inner_dict = {}
        inner_dict["type"] = "section"

        text_dict = {}
        inner_text_dict = {}
        inner_text_dict["type"] = "mrkdwn"
        inner_text_dict["text"] = "\t*" + model + "*\n _Dataset description_ \n Trained models: \n"

        for trained_model in trained_models:
            inner_text_dict["text"] += "\t{}\n".format(trained_model)

        inner_dict["text"] = inner_text_dict
        inner_blocks.append(inner_dict)
        inner_blocks.append({"type": "divider"})

    select_block = {}
    select_block["type"] = "section"
    select_block["text"] = {
        "text": "Select a model",
        "type": "mrkdwn"
    }
    inner_select = {}
    inner_select["action_id"] = "select_model"
    inner_select["type"] = "static_select"
    inner_select["placeholder"] = {
        "type": "plain_text",
        "text": "Select"
    }

    options_dicts = []
    for model in models:
        trained_models = os.listdir("../framework/model/models/" + model)
        options_dicts.append({
            "text": {
                "type": "plain_text",
                "text": "----- {} -----".format(model)
            },
            "value": "none"
        })
        for trained_model in trained_models:
            options_dicts.append({
                "text": {
                    "type": "plain_text",
                    "text": trained_model
                },
                "value": model + "|" +trained_model
            })

    inner_select["options"] = options_dicts
    select_block["accessory"] = inner_select
    inner_blocks.append(select_block)
            
    outer["blocks"] = inner_blocks
    #outer["channel"] = "#random"
    return outer
        


def sendMessage(msg):
    url = "https://hooks.slack.com/services/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"
    # post = { "text": "{0}".format(msg) }
    post = msg
    jsoned = json.dumps(post)
    encoded_data = jsoned.encode('ascii')
    print(post)
    print("----")
    print(encoded_data)
    headers = { 'Content-Type': 'application/json', 'X-Slack-No-Retry': '1' }

    try:
        req = request.Request(url, data=encoded_data, headers=headers)
        resp = request.urlopen(req)
    except Exception as em:
        print("EXCEPTION: " + str(em))

def do_bot_command(text):
    if "!load" in text:
        pass
    elif "!list" in text or "!models" in text:
        model_list = os.listdir("../framework/model/models")
        msg = createModelList(model_list)
        print(msg)
        sendMessage(msg)
    elif "!help" in text:
        pass

global a
a=0
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        if a == 0:
            self.model_group = "movie"
            self.model_name = "movie3"

        self.model = ExtractionModel(self.model_group, self.model_name)
        super().__init__(*args, **kwargs)

    def switch_model(model_str):
        a=1
        modelgrp = model_str.split("|")
        self.model_group = modelgrp[0]
        self.model_name = modelgrp[1]

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        self.send_response(200)
        content_length = int(self.headers['Content-Length'])

        retries = self.headers['X-Slack-Retry-Num']
        #print(self.headers['X-Slack-Retry-Reason'])

        if retries != None:
            print("Slack retry num: " + self.headers['X-Slack-Retry-Num'])
            self.send_response(200)
            return
        
        body = self.rfile.read(content_length)
        if b'payload' in body:
            body = unquote(str(body),encoding='utf-8')
            body= body.replace("payload=", "")
            body = body.replace("b'", "")
            body = body[:-1]
            json_data = json.loads(body)
            selected_model = json_data["actions"][0]["selected_option"]["value"]
            self.switch_model(selected_model.split("|"))
        else:
            json_data = json.loads(body.decode('utf-8'))
            self.end_headers()

            if json_data["type"] == "url_verification":
                response = BytesIO()
                response.write(b'This is POST request. ')
                response.write(b'Received: ')
                response.write(body)
                self.wfile.write(response.getvalue())
                self.send_response(200)
                return

            if json_data["event"]["type"] == "message":
                #print("---- Test -----")
                #print(json_data["event"]["text"][0])
                if json_data["event"]["text"][0] != "!":
                    #model = ExtractionModel("movie", "movie3")
                    extraction = self.model.extract(json_data["event"]["text"])
                    print()
                    print("---MODEL OUTPUT---")
                    print(extraction)
                    str_k = ""
                    keys = []
                    for k in extraction:
                        keys.append(k)
                    print("\n---KEYS---")
                    print(keys)
                    print("\n\n")
                    for i in range(len(keys)-1):
                        print(i)
                        if extraction[keys[i]][0] != 'O':
                            entity = extraction[keys[i]][0].split('-')[1]
                            if (i < len(keys) - 2) and (extraction[keys[i+1]][0] != 'O'):
                                next_entity = extraction[keys[i+1]][0].split('-')[1]
                            else:
                                str_k += ('*'+keys[i]+'* '+'`'+entity+'` ')
                                continue
                            if entity == next_entity:
                                str_k += ('*'+keys[i]+'* ')
                            else:
                                str_k += ('*'+keys[i]+'* '+'`'+entity+'` ')
                        else:
                            str_k += (keys[i] + ' ')
                    response = createBlockMessage(str_k)
                    pprint(response)
                    sendMessage(response)
                else:
                    do_bot_command(json_data["event"]["text"])
                return
                    

httpd = HTTPServer(('localhost', 8001), SimpleHTTPRequestHandler)
httpd.serve_forever()
#print(createModelList(os.listdir("../framework/model/models/")))