from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({'message' : 'hello world'})

@app.route('/get_param', methods=['GET']) #test get param
def get_param():
    param = request.get_json()
    return jsonify(param)

@app.route('/acknowledgement_activity')
def get_activity():
    type_param = request.args.get('activity_type')
    status_param = request.args.get('status')

    data = {} #to return

    conn = sqlite3.connect('acknowledge.db')
    c = conn.cursor()


    if type_param is not None and status_param is None:
        c.execute('SELECT * FROM acknowledgement_activity WHERE activity_type=?', (type_param,))
        #print(c.fetchall())
        data = arrange_data(c.fetchall())
    elif type_param is None and status_param is not None:
        c.execute('SELECT * FROM acknowledgement_activity WHERE status=?', (status_param,))
        #print(c.fetchall())
        data = arrange_data(c.fetchall())
    elif type_param is not None and status_param is not None:
        c.execute('SELECT * FROM acknowledgement_activity WHERE activity_type=? AND status=?', (type_param, status_param))
        #print(c.fetchall())
        data = arrange_data(c.fetchall())
    else:
        c.execute('SELECT * FROM acknowledgement_activity')
        #print(c.fetchall())
        data = arrange_data(c.fetchall())
    

    conn.close()
    return data

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
    
    df = pd.DataFrame({'activity':activity, 'activity_type':activity_type, 'status':status, 'reported_datetime':reported_datetime, 'acknowledged_datetime':acknowledged_datetime, 'user':user})
    #print(df)
    return jsonify({'data' : df.to_dict()})
    


if __name__ == '__main__':
    app.run(debug=True)