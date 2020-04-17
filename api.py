#!/usr/bin/python

from flask import Flask, jsonify
from flask import request
from flask_restplus import Resource, Api
import requests
import sqlite3
from flask_cors import CORS
import pandas as pd
from datetime import datetime
import json
from random import randint
#from pandas.io.json import json_normalize

#counters numbers
#http://34.87.233.248:5000

LOANS='A'
ACCOUNTS='B'
CHEQUES='C'
EXCHANGE='D'
GENERAL_INFO='E'
ATM='F'
num_people_served = 0;

app = Flask(__name__)
CORS(app)
api = Api(app)

conn = sqlite3.connect('data.db')
cur = conn.cursor()
#cur.execute('Drop table customers')
cur.execute('create table if not exists dynamic_queue (`index` int, name varchar, customer_id varchar, service varchar, ticket varchar, counter varchar)')
cur.execute('create table if not exists analytics (`index` int, name varchar, customer_id varchar, service varchar, ticket varchar, counter varchar)')
cur.execute('create table if not exists customers (`index` int, name varchar, customer_id varchar, password varchar)')
cur.execute('create table if not exists feedbacks (`index` int, customer_id varchar, feedback varchar)')

conn.commit()
conn.close()


@api.route('/queue', methods=['POST'])
@api.doc(params={'queue_data': 'sample :- {\"name\": \"blah\", \"customer_id\": \"blah\", \"service\": \"nameofservice\"} \n services =[accounts, loans, exchange, atm, cheques, general]'})
@api.doc(params={'customer_data': 'ex.{\"name\": \"blah\", \"password\": \"blah\"}'})
@api.doc(params={'feedback_data': 'ex.{\"customer_id\": \"blah\", \"feedback\": \"Poor/Okay/Good/Excellent/Outstanding\"}'})

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
			df.to_sql('analytics', if_exists='append', con=conn)
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

			res ={
				"Feedback": "received"
				}
			return 200

		else:
			res={
				"Error": "Incorrect input"
			}
			return res, 404

@api.route('/queue/<ticket>', methods=['DELETE'])
class delete(Resource):
	def delete(self, ticket):

		conn = sqlite3.connect('data.db')
		cur = conn.cursor()

		cur.execute('select * from dynamic_queue where ticket ='+ticket)
		result = cur.fetchall()

		if result == []:
			task={
				"Error": "No entry with Id "+ticket+" Found!"
			}
			return task, 404

		cur.execute('Delete from dynamic_queue where ticket ='+ticket)
		conn.commit()
		num_people_served = num_people_served +1;
		conn.close()

		return res, 200

@api.route('/show/servedpeople', methods=['GET'])
class GetInfo(Resource):
	def get(self):
		res ={
			"num_people_served": str(num_people_served)
		}

		return res, 200

@api.route('/show/alltickets', methods=['GET'])
class GetInfo(Resource):
	def get(self):
		conn = sqlite3.connect('data.db')
		cur = conn.cursor()

		cur.execute('select * from dynamic_queue')
		result = cur.fetchall()

		if result == []:
			task={
				"Error": "empty queue"
			}
			return task, 404

		tickets = []
		for i in result:
			task = {
						"name": str(i[1]),
						"service": str(i[3]),
						"ticket": str(i[4]),
						"counter": str(i[5])
					}
			tickets.append(task)
		#conn.commit()
		res = {"alltickets":tickets}
		conn.close()

		return res, 200

@api.route('/show/logs', methods=['GET'])
class GetInfo(Resource):
	def get(self):
		conn = sqlite3.connect('data.db')
		cur = conn.cursor()

		cur.execute('select * from analytics')
		result = cur.fetchall()

		if result == []:
			task={
				"Error": "empty queue"
			}
			return task, 404

		lengthoflogs = len(result)

		cur.execute('select * from analytics where counter= "A"')
		result = cur.fetchall()
		lengthofloans = (len(result)/lengthoflogs)*100

		cur.execute('select * from analytics where counter= "B"')
		result = cur.fetchall()
		lengthofaccounts = (len(result)/lengthoflogs)*100

		cur.execute('select * from analytics where counter= "C"')
		result = cur.fetchall()
		lengthofcheques = (len(result)/lengthoflogs)*100

		cur.execute('select * from analytics where counter= "D"')
		result = cur.fetchall()
		lengthofexchange = (len(result)/lengthoflogs)*100

		cur.execute('select * from analytics where counter= "E"')
		result = cur.fetchall()
		lengthofgeneral = (len(result)/lengthoflogs)*100

		cur.execute('select * from analytics where counter= "F"')
		result = cur.fetchall()
		lengthofatm = (len(result)/lengthoflogs)*100


		res = {
			"total" : str(lengthoflogs),
			"accounts":str(lengthofaccounts),
			"loans":str(lengthofloans),
			"exchange":str(lengthofexchange),
			"general":str(lengthofgeneral),
			"atm":str(lengthofatm),
			"cheques":str(lengthofcheques)
		}
		conn.close()

		return res, 200


@api.route('/show/feedback', methods=['GET'])
class GetInfo(Resource):
	def get(self):
		conn = sqlite3.connect('data.db')
		cur = conn.cursor()

		
		cur.execute('select * from feedbacks')
		result = cur.fetchall()
		print(result)
		if result == []:
			task={
				"Error": "No Feedbacks Received Yet."
			}
			return task, 404

		cur.execute('select * from feedbacks where feedback="Poor"')
		result = cur.fetchall()
		poor = len(result)
		cur.execute('select * from feedbacks where feedback="Okay"')
		result = cur.fetchall()
		okay = len(result)
		cur.execute('select * from feedbacks where feedback="Good"')
		result = cur.fetchall()
		good = len(result)
		cur.execute('select * from feedbacks where feedback="Excellent"')
		result = cur.fetchall()
		excellent = len(result)
		cur.execute('select * from feedbacks where feedback="Outstanding"')
		result = cur.fetchall()
		outstanding = len(result)

		res = {
			"Poor" : str(poor),
			"Okay" : str(okay),
			"Good" : str(good),
			"Excellent" : str(excellent),
			"Outstanding" : str(outstanding)
			}
		conn.close()

		return res, 200

@api.route('/auth', methods=['POST'])
@api.doc(params={'customer_id': 'Ex. 55555'})
@api.doc(params={'password': 'Ex. Pass123'})
class authenticate(Resource):
	def post(self):
		password = request.args.get('customer_id')
		username = request.args.get('password')
		conn = sqlite3.connect('data.db')
		cur = conn.cursor()
		cur.execute("select * from customers where password='"+str(password)+"' and customer_id='"+str(username)+"'")
		result = cur.fetchall()

		if result == []:
			res = {
					"Error": "Invalid customer ID or password"
				}	
			return res, 404
		else:
			res={
					"statusOK" : "Access can be granted"
				}
			return res, 200


def GenerateCustomerId():
	return randint(10000, 99999)

def GenerateTicket():
	return randint(100,999)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
