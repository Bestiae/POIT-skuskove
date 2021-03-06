from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import MySQLdb 
# import mysql.connector      
import math
import time
import configparser as ConfigParser
import random

async_mode = None

app = Flask(__name__)


config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 


def background_thread(args):
    count = 0  
    dataCounter = 0 
    dataList = []  
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    # db = mysql.connector.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    while True:
        if args:
          A = dict(args).get('A')
          dbV = dict(args).get('db_value')
        else:
          A = 1
          dbV = 'nieco'  
        print(dbV) 
        print(args)  
        socketio.sleep(2)
        count += 1
        dataCounter +=1
        prem = random.random()
        if dbV == 'start':
          # dataDict = {
          #   "t": time.time(),
          #   "x": dataCounter,
          #   "y": float(A)*prem}
          # dataList.append(dataDict)
          dataDict = {
            "t": time.time(),
            "x": dataCounter,
            "ys": A*math.sin(dataCounter),
            "yc": A*math.cos(dataCounter)
          }
          dataList.append(dataDict)
        else:
          if len(dataList)>0:
            fuj = str(dataList).replace("'", "\"")
            print(fuj)
            cursor = db.cursor()
            
            cursor.execute("SELECT MAX(id) FROM sin_cos")
            maxid = cursor.fetchone()

            # cursor.execute("INSERT INTO graph (id, hodnoty) VALUES (%s, %s)", (maxid[0] + 1, fuj))
            # uloha 1 sinus kosinus
            cursor.execute("INSERT INTO sin_cos (id, sin_cos) VALUES (%s, %s)", (maxid[0] + 1, fuj))
            db.commit()
          dataList = []
          dataCounter = 0
        socketio.emit('my_response',
                      {'data': float(A)*prem, 'sinus': A*math.sin(dataCounter), 'cosinus': A*math.cos(dataCounter), 'count': count},
                      namespace='/test')  
    db.close()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    return render_template('graph.html', async_mode=socketio.async_mode)
    
@app.route('/db')
def db():
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  # cursor.execute('''SELECT  hodnoty FROM  graph WHERE id=1''')
  cursor.execute('''SELECT * FROM sin_cos''')
  rv = cursor.fetchall()
  return str(rv)    

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print(num)
  # cursor.execute("SELECT hodnoty FROM  graph WHERE id=%s", num)
  cursor.execute("SELECT sin_cos FROM sin_cos WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])
    
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})

@socketio.on('db_event', namespace='/test')
def db_message(message):   
#    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['db_value'] = message['value']    
#    emit('my_response',
#         {'data': message['value'], 'count': session['receive_count']})

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
   # emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
