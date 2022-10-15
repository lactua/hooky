from time import sleep
from flask import Flask, request
from requests import post, get
from threading import Thread
from os import mkdir
from os.path import exists
from json import dump, load
from random import choices
from string import ascii_letters

HOST = ('45.158.77.206', 80)

def genKey(length=9): return ''.join(choices(ascii_letters, k=length))

def writeDB():
    global db
    while True:
        with open('src/db.json', 'w') as file:
            dump(db, file, indent=4)
        sleep(0.5)

def init():
    global db, app

    if not exists('src'):
        mkdir('src')

    if not exists('src/db.json'):
        with open('src/db.json', 'w') as file:
            file.write('{}')

    with open('src/db.json', 'r') as file:
        db = load(file)

    writeDBThread = Thread(target=writeDB)
    writeDBThread.start()

    app = Flask('app')

def main():
    global app

    init()

    @app.route('/new', methods=['POST'])
    def _new():

        global db

        webhook = request.json.get('webhook')

        if type(webhook) != str:
            return 'Bad Request', 400

        if not webhook.startswith('https://discord.com/api/webhooks'):
            return 'Bad Request', 400
        
        if get(webhook).status_code != 200:
            return 'Bad Request', 400 

        key = genKey()        
        
        db[key] = webhook

        return f'http://hooky.ddns.net/send/{key}'

    @app.route('/send/<key>', methods=['POST'])
    def _send(key):

        global db

        json = request.json

        if not db.get(key):
            return 'Not found', 404

        res = post(db[key], json=json)

        return res.text, res.status_code

    app.run(*HOST)

if __name__ == '__main__':
    main()


from urllib import request

request.Request()