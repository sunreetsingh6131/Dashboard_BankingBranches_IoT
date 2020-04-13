#!/usr/bin/python

from flask import Flask, jsonify
from flask import request
from flask_restplus import Resource, Api
import requests
import sqlite3
import pandas as pd
from datetime import datetime
import json
#from pandas.io.json import json_normalize

#counters numbers
LOANS='A'
ACCOUNTS='B'
CHEQUES='C'
EXCHANGE='D'
GENERAL_INFO='E'
ATM='F'

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect('data.db')
cur = conn.cursor()
#cur.execute('create table if not exists collections (`index` int, countryiso3code char, date integer, value float, indicator varc>
#conn.commit()
conn.close()



#{'name': "blah", 'service': "blah", 'ticket_number': 123}

@api.route('/queue', methods=['POST'])
@api.doc(params={'queue_data': 'ex.{\"name\": \"blah\", \"customer_id\": \"blah\", \"service\": \"nameofservice\"}'})
@api.doc(params={'customer_data': 'ex.{\"name\": \"blah\", \"email\": \"blah\"}'})
@api.doc(params={'feedback_data': 'ex.{\"customer_id\": \"blah\", \"feedback\": \"blah\"}'})

class Collections(Resource):
	
	def post(self):
		if request.args.get('queue_data') != None:
			data = request.args.get('queue_data')
			print(data)
			jsondata = json.loads(data)

			df = pd.DataFrame(jsondata, index=[0])
			print(df)

			conn = sqlite3.connect('data.db')
			cur = conn.cursor()
			#cur.execute('delete from dynamic_queue where name="Johnny"')
			df.to_sql('dynamic_queue', if_exists='append', con=conn)
			conn.commit()

			df = pd.read_sql('select * from dynamic_queue', con=conn)
			print(df)

			conn.close()
			# return ticket number and service counter

			# ticket
			# counter
			# res={
			# 		'ticket': ticket,
			# 		'counter': counter
			# 	}
		elif request.args.get('customer_data') != None:
			print("here")
		elif request.args.get('feedback_data') != None:
			print("herer")
		return 200


# @api.route('/queue', methods=['POST'])
# @api.doc(params={'customer_data': 'ex.{\"name\": \"blah\", \"customer_id\": \"blah\", \"service\": \"nameofservice\"}'})
# class Collections(Resource):
# 	def post(self):
# 		data = request.args.get('data')
# 		print(data)
# 		jsondata = json.loads(data)
# 		print(jsondata)

# 		return 200
# 		#conn = sqlite3.connect('data.db')
# 		#cur = conn.cursor()
# 		#conn.commit()
# 		#conn.close()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
