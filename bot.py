import os
import json
import requests
from flask import Flask, request


PAGE_ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']


app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        print("Verified")
        return request.args.get('hub.challenge', '')
    else:
        print('wrong verification token')
        return "Error, Verification Failed"
    return "Hello world", 200


@app.route('/', methods=['POST'])
def handle_messages():
    data = request.get_json()
    entry = data['entry'][0]
    if entry.get("messaging"):
        messaging_event = entry['messaging'][0]
        sender_id = messaging_event['sender']['id']
        message_text = messaging_event['message']['text']
        send_gif_message(sender_id, message_text)
    return 'ok', 200


def search_gif(text):
    payload = {'s': text, 'api_key': os.environ['API_KEY']}
    r = requests.get('http://api.giphy.com/v1/gifs/translate', params=payload)
    r = r.json()
    url = r['data']['images']['original']['url']

    return url


def send_gif_message(recipient_id, message):
    gif_url = search_gif(message)

    print(gif_url)
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": gif_url
                }
            }}
    })

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)

    print(r)

if __name__ == '__main__':
    app.run(debug=True)
