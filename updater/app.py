from flask import Flask, render_template, request
import redis

red = redis.Redis(host='hydr0.com')

@app.route('/hook/', methods=['POST'])
def hook_view():
    print request.json
    red.publish('irc.m', json.dumps({'tag':'UPD'}))