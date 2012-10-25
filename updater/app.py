from flask import Flask, render_template, request
import redis, json, os

red = redis.Redis(host='hydr0.com')
app = Flask(__name__)

@app.route('/hook/', methods=['POST'])
def hook_view():
    if request.json['ref'] == 'refs/heads/deploy':
        print 'Sending update'
        i = request.json['commits'][-1]
        if len(request.json['commits']) > 1: plural = 's'
        else: plural = ''
        m = '%s (%s commit%s pushed by %s)' % (i['message'], len(request.json['commits']), plural, i['author']['name'])
        red.publish('irc.m', json.dumps({'tag':'UPD', 'msg':m}))
        os.popen('screen -S master -X kill')
        os.popen('git pull origin deploy')
        os.popen('screen -dmS master exec "cd ../master/; python start.py"')
    return ':)'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9010)