from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({'message' : 'hello world'})

@app.route('/test_req', methods=['GET']) #test get req
def get_body():
    req = request.get_json()
    return jsonify(req)

@app.route('/get', methods=['GET'])
def get():
    type_param = request.args.get('type')
    status_param = request.args.get('status')

    conn = sqlite3.connect('acknowledge.db')
    c = conn.cursor()


    if type_param is not None and status_param is None:
        c.execute('SELECT * FROM acknowledgement_activity WHERE activity_type=?', (type_param,))
        #print(c.fetchall())
        data = arrange_data(c.fetchall())

        conn.close()
        return data #already jsonified
    elif type_param is None and status_param is not None:
        c.execute('SELECT * FROM acknowledgement_activity WHERE status=?', (status_param,))
        #print(c.fetchall())
        data = arrange_data(c.fetchall())

        conn.close()
        return data #already jsonified
    elif type_param is not None and status_param is not None:
        c.execute('SELECT * FROM acknowledgement_activity WHERE activity_type=? AND status=?', (type_param, status_param))
        #print(c.fetchall())
        data = arrange_data(c.fetchall())

        conn.close()
        return data #already jsonified
    else:
        c.execute('SELECT * FROM acknowledgement_activity')
        #print(c.fetchall())
        data = arrange_data(c.fetchall())

        conn.close()
        return data #already jsonified

def arrange_data(result):
    activity = []
    activity_type = []
    status = []
    reported_datetime = []
    acknowledged_datetime = []
    user = []

    for res in result:
        activity.append(res[0])
        activity_type.append(res[1])
        status.append(res[2])
        reported_datetime.append(res[3])
        acknowledged_datetime.append(res[4])
        user.append(res[5])
    
    return jsonify({'activity': activity, 'activity_type':activity_type, 'status':status, 'reported_datetime':reported_datetime, 'acknowledged_datetime':acknowledged_datetime, 'user':user})

@app.route('/update', methods=['PUT'])
def update():
    name_param = request.args.get('name')
    status_param = request.args.get('status')

    conn = sqlite3.connect('acknowledge.db')
    c = conn.cursor()

    if name_param is not None and status_param is not None:
        if status_param not in ['pending', 'acknowledged']:
            return jsonify({'message': 'invalid status to update'})
        
        c.execute('SELECT COUNT(*) FROM acknowledgement_activity WHERE activity = ?',(name_param,))

        if c.fetchone()[0] == 1:
            c.execute('UPDATE acknowledgement_activity SET status = ? WHERE activity=?', (status_param, name_param))
            conn.commit()
            conn.close()
            return jsonify({'message': f'activity {name_param} has been updated to {status_param}'})
        else:
            return jsonify({'message': f'could not find activity {name_param}'})
    else:
        return jsonify({'message': 'no parameters'})
    
@app.route('/acknowledge', methods=['PUT'])
def acknowledge():
    name_param = request.args.get('name')

    conn = sqlite3.connect('acknowledge.db')
    c = conn.cursor()

    if name_param is not None:
        c.execute('SELECT COUNT(*) FROM acknowledgement_activity WHERE activity = ? AND status=?',(name_param,'pending'))

        if c.fetchone()[0] == 1:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
            c.execute('UPDATE acknowledgement_activity SET status = ?, acknowledged_datetime = ? WHERE activity=?', ('acknowledged', formatted_time, name_param))
            conn.commit()
            conn.close()
            return jsonify({'message': f'activity {name_param} has been acknowledged'})
        else:
            conn.close()
            return jsonify({'message': f'could not find pending activity {name_param}'})
    else:
        return jsonify({'message': 'no/invalid parameters'})

if __name__ == '__main__':
    app.run(debug=True)
