from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit,jsonify, join_room, leave_room, \
    close_room, rooms, disconnect
import requests
import json
from elasticsearch import Elasticsearch
async_mode = None

application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(application, async_mode=async_mode)
thread = None
chab = ""

def parse_tweets(msg):
    msg_doc= {}
    msg2 = json.loads(msg)
    print "FINAL RUN"
    print "MSG2 IS"
    print type(msg2)
    print "MSG2 COORD IS"
    print type(msg2['coordinates'])
    msg3 = json.loads(msg2['coordinates'])
    print "MSG2 COORD COORD IS"
    print type(msg3['coordinates'])
    print "1st ELEMENT"
    print msg3['coordinates'][0]
    msg_doc['positionx'] = msg3['coordinates'][1]
    msg_doc['positiony'] = msg3['coordinates'][0]
    msg_doc['type'] = msg2['sentiment']
    msg_doc['title'] = msg2['text']
    msg_doc['id'] = msg2['id']
    return msg_doc


def parse(resul):
    for rl in resul['hits']['hits']:
        rl['_source']['text'] = ''.join(i for i in rl['_source']['text'] if ord(i)<128)
    return resul


def msg_process(msg, tstamp):
    print "trying to find the error"
    print msg
    msg=parse_tweets(msg)
    es = Elasticsearch([{'host': 'search-tweets-cxx6vzzzsobvc3ipbzrk3dreky.us-west-2.es.amazonaws.com', 'port': 443, 'use_ssl': True}])
    es.index(index='senti_twitter', doc_type='senti_tweets', id=msg['id'], ttl="4d", body=msg)
    socketio.emit('my_response',
                  {'title': msg['title'], 'type':msg['type'],'positionx':msg['positionx'],'positiony':msg['positiony']},
                  namespace='/test')

def tweetmatch(elsr, key):
    if len(key) is 0:
        r = elsr.search(size=5000,index='senti_twitter')
    else:
        r = elsr.search(size=5000, index="senti_twitter", body={"query": {"query_string": {"query": key}}})
    return r


@application.route('/', methods=['GET', 'POST', 'PUT'])
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

def updateKeyList(keyList):
    global chab
    chab = keyList


@application.route('/ks', methods=['GET', 'POST'])
def ks():
    key = str(request.form['keyword'])
    updateKeyList(key)
    elsr = Elasticsearch([{'host': 'search-tweets-cxx6vzzzsobvc3ipbzrk3dreky.us-west-2.es.amazonaws.com',
                           'port': 443, 'use_ssl': True}])
    result = tweetmatch(elsr, str(key))
    retresult = parse(result)
    return jsonify(retresult)





@application.route('/trying', methods=['GET', 'POST', 'PUT'])
def sns():
    # AWS sends JSON with text/plain mimetype
    try:
        js = json.loads(request.data)


    except Exception, e:
        print "Exception here"

    print "I am here"
    hdr = request.headers.get('X-Amz-Sns-Message-Type')
    # subscribe to the SNS topic
    if hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
        r = requests.get(js['SubscribeURL'])

    if hdr == 'Notification':
        msg_process(js['Message'], js['Timestamp'])

    return 'OK\n'
#
# if  __name__ == '__main__':
#     application.run(
#         host="0.0.0.0",
#         port=80,
#         debug=True)
#

if __name__ == '__main__':
    socketio.run(application,host='0.0.0.0', port=80, debug=True)
