import os
import sys
import json
import requests

from kova import *
from flask import Flask, request

app = Flask(__name__)

"""
Shout out to Hartley Brody who developed a Python sample project for Facebook Messenger.
"""

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Lena Kova is developed by Junwon Park at Stanford University.", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing
    print data
    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if "text" in messaging_event["message"].keys():
                        message = messaging_event["message"]["text"]  # the message's text
                        process_message(message, sender_id)
                    else:
                        attachment = messaging_event["message"]["attachments"]  # the message's image
                        message = attachment[1]["url"] #url of content
                        message_type = attachment[0]
                        if message_type != "video" and message_type != "audio" and message_type != "file":
                            message_type = "image"
                        send_message(sender_id, message, message_type)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def process_message(message_text, sender_id):
    kova = Kova()
    kova.chat(message_text, sender_id)

def send_message(recipient_id, message, message_type):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    if message_type == "text":
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message
            }
        })
    else:
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment":{
                  "type": message_type,
                  "payload":{
                    "url": message
                  }
                }
            }
        })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
