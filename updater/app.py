from flask import Flask, render_template, request
import redis, json

red = redis.Redis(host='hydr0.com')
app = Flask(__name__)

@app.route('/hook/', methods=['POST'])
def hook_view():
    if request.json['ref'] == '/ref/heads/deploy':
        i = request.json['commits'][-1]
        if len(i['commits']) > 1: plural = 's'
        else: plural = ''
        m = '%s (%s commit%s pushed by %s)' % (i['message'], len(i['commits']), plural, i['author']['name'])
        red.publish('irc.m', json.dumps({'tag':'UPD', 'msg':m}))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9010)