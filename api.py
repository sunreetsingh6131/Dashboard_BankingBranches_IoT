#!/usr/bin/python

from flask import Flask, jsonify
from flask import request
from flask_restplus import Resource, Api
import requests
import sqlite3
import pandas as pd
from datetime import datetime
import json
from random import randint
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
#cur.execute('Drop table customers')
cur.execute('create table if not exists dynamic_queue (`index` int, name varchar, customer_id varchar, service varchar, ticket varchar, counter varchar)')
cur.execute('create table if not exists customers (`index` int, name varchar, customer_id varchar, email varchar, password varchar)')
cur.execute('create table if not exists feedbacks (`index` int, customer_id varchar, feedback varchar)')
conn.commit()
conn.close()


@api.route('/queue', methods=['POST'])
@api.doc(params={'queue_data': 'sample :- {\"name\": \"blah\", \"customer_id\": \"blah\", \"service\": \"nameofservice\"} \n services =[accounts, loans, exchange, atm, cheques, general]'})
@api.doc(params={'customer_data': 'ex.{\"name\": \"blah\", \"email\": \"blah\", \"password\": \"blah\"}'})
@api.doc(params={'feedback_data': 'ex.{\"customer_id\": \"blah\", \"feedback\": \"blah\"}'})

class Collections(Resource):
	
	def post(self):
		if request.args.get('queue_data') != None:
			data = request.args.get('queue_data')
			print(data)
			jsondata = json.loads(data)

			df = pd.DataFrame(jsondata, index=[0])

			conn = sqlite3.connect('data.db')
			cur = conn.cursor()

			while True:
				ticket_generator = GenerateTicket()
				cur.execute("select * from dynamic_queue where ticket = '"+str(ticket_generator)+"'")
				duplicate_ticket = cur.fetchone()

				if duplicate_ticket == None:
					ticket = str(ticket_generator)
					df['ticket'] = ticket
					service = ""
					if df['service'].str.contains('loans').any():
						service = LOANS
						df['counter'] = service

					elif df['service'].str.contains('accounts').any():
						service = ACCOUNTS
						df['counter'] = service
					
					elif df['service'].str.contains('cheques').any():
						service = CHEQUES
						df['counter'] = service
					
					elif df['service'].str.contains('exchange').any():
						service = EXCHANGE
						df['counter'] = service
					
					elif df['service'].str.contains('general').any():
						service = GENERAL_INFO
						df['counter'] = service
					
					elif df['service'].str.contains('atm').any():
						service = ATM
						df['counter'] = service

					break

			df.to_sql('dynamic_queue', if_exists='append', con=conn)
			conn.commit()

			temp_df = pd.read_sql('select * from dynamic_queue', con=conn)
			print(temp_df)

			conn.close()

			res={
					'ticket': ticket,
					'counter': service
				}
			return res, 200

		elif request.args.get('customer_data') != None:
			data = request.args.get('customer_data')
			jsondata = json.loads(data)
			df = pd.DataFrame(jsondata, index=[0])
			conn = sqlite3.connect('data.db')
			cur = conn.cursor()
			customerIdGenerator = GenerateCustomerId()

			while True:
				customer_id = str(GenerateCustomerId())
				cur.execute("select * from customers where customer_id = '"+customer_id+"'")
				duplicate_id = cur.fetchone()
				if duplicate_id == None:
					 df['customer_id'] = customer_id
					 break

			df.to_sql('customers', if_exists='append', con=conn)
			conn.commit()
			temp_df = pd.read_sql('select * from customers', con=conn)
			print(temp_df)
			conn.close()

			res={
					'customer_id': customer_id
				}
			return res, 200

		elif request.args.get('feedback_data') != None:
			data = request.args.get('feedback_data')
			jsondata = json.loads(data)
			df = pd.DataFrame(jsondata, index=[0])
			conn = sqlite3.connect('data.db')
			cur = conn.cursor()
			df.to_sql('feedbacks', if_exists='append', con=conn)
			conn.commit()
			temp_df = pd.read_sql('select * from feedbacks', con=conn)
			print(temp_df)
			conn.close()
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

def GenerateCustomerId():
	return randint(10000, 99999)

def GenerateTicket():
	return randint(100,999)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)