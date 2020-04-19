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
import numpy as np
from pandas import read_csv
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.ar_model import ARResults
import pytz



""" API FOR BLUETOOTH BEACON CONNECTIVITY FOR BANK BRANCHES VIA APP. """
""" Connects mobile app to bank's dashboard for queue management and data collection for Analytics """
""" API(in flask restplus) - http://34.87.233.248:5000 """
""" DASHBOARD - http://34.87.233.248:3000 """

LOANS='A'
ACCOUNTS='B'
CHEQUES='C'
EXCHANGE='D'
GENERAL_INFO='E'
ATM='F'
num_people_served = 0;
mean_array = []

app = Flask(__name__)
CORS(app)
api = Api(app)

conn = sqlite3.connect('data.db')
cur = conn.cursor()
#cur.execute('Drop table dynamic_queue')
cur.execute('create table if not exists dynamic_queue (`index` int, name varchar, customer_id varchar, service varchar, ticket varchar, counter varchar)')
cur.execute('create table if not exists analytics (`index` int, name varchar, customer_id varchar, service varchar, ticket varchar, counter varchar)')
cur.execute('create table if not exists customers (`index` int, name varchar, customer_id varchar, password varchar)')
cur.execute('create table if not exists feedbacks (`index` int, customer_id varchar, feedback varchar)')
cur.execute('create table if not exists timelog (`index` int, time timestamp)')
conn.commit()
conn.close()



"""
	endpoint '/queue' with POST statements for API.
	
	Takes three different query parameters taking string in JSON format
	1) queue_data : Adds customer to Queue. Returns JSON object with ticket number and counter number. 
				sample example =  {"customer_id": "11472", "service": "loans"}

	2) customer_data : Adds customer to database(like signup) and returns json object with unique customer_id
				sample example =  {"name": "John Smith", "password": "password123"}

	3) feedback_data : Adds feedback to database.
				sample example =  {"customer_id": "11472", "feedback": "Good"}
"""

@api.route('/queue', methods=['POST'])
@api.doc(params={'queue_data': 'sample :- {\"customer_id\": \"blah\", \"service\": \"nameofservice\"} \n services =[accounts, loans, exchange, atm, cheques, general]'})
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

			cust = df['customer_id'][0]
			cur.execute('select * from customers where customer_id = "'+str(cust)+'"')
			result = cur.fetchall()
			df['name'] = result[0][1]

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

			new_df=pd.DataFrame(columns=['time'])
			time = pd.Timestamp.now(tz="Australia/Sydney")
			new_df.loc[0]= time
			print(time)
			new_df.to_sql('timelog', if_exists='append', con=conn)
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


"""
	endpoint '/queue/{id}' with DELETE statement for API.
	
	Deletes the customer from the queue when customer representative has served the customer.
	
"""

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
		conn.close()
		global num_people_served
		num_people_served = num_people_served +1;
		
		return 200


"""
	endpoint '/show/servedpeople' with GET statement for API.
	
	Gets info about number of people dealt with on that day. Returns them in JSON format.

"""
@api.route('/show/servedpeople', methods=['GET'])
class GetInfo(Resource):
	def get(self):
		global num_people_served
		print(num_people_served)
		res ={
			"num_people_served": str(num_people_served)
		}

		return res, 200

"""
	endpoint '/show/alltickets' with GET statement for API.
	
	Gets all the active tickets. Returns them in JSON format.
	
"""
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

"""
	endpoint '/show/logs' with GET statement for API.
	
	Gets count of customers that visited particular counter. returns the counts in JSON format.
	
"""

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


"""
	endpoint '/show/feedback' with GET statement for API.
	
	Gets all the feedback given by customers. returns the counts in JSON format.
	
"""
@api.route('/show/feedback', methods=['GET'])
class GetInfo(Resource):
	def get(self):
		conn = sqlite3.connect('data.db')
		cur = conn.cursor()

		
		cur.execute('select * from feedbacks')
		result = cur.fetchall()
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


"""
	endpoint '/auth' with POST statement for API.
	
	Authorises the login on app. returns success/error as response.
	Takes two query paramters, 'customer_id' and 'password'

"""
@api.route('/auth', methods=['POST'])
@api.doc(params={'customer_id': 'Ex. 55555'})
@api.doc(params={'password': 'Ex. Pass123'})
class authenticate(Resource):
	def post(self):
		password = request.args.get('password')
		username = request.args.get('customer_id')
		print(password)
		print(username)
		conn = sqlite3.connect('data.db')
		cur = conn.cursor()
		cur.execute("select * from customers")
		result = cur.fetchall()
		print(result)
		cur.execute("select * from customers where password='"+password+"' and customer_id='"+username+"'")
		result = cur.fetchall()
		cur.close()
		print(result)
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


"""
	endpoint '/show/predictions' with GET statement for API.
	
	Gets all the predictions about busyness week around with 95% Confidence Interval. 
	returns the prediction counts in JSON format.
	
"""
@api.route('/show/predictions', methods=['GET'])
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

		cur.close()

		mydates = pd.date_range(datetime.today(), periods=1000).tolist()
		Loan = np.random.poisson(lam = int(lengthofloans), size = len(mydates))
		Exchange = np.random.poisson(lam = int(lengthofexchange), size = len(mydates))
		ATM = np.random.poisson(lam = int(lengthofatm), size = len(mydates))
		Accounts = np.random.poisson(lam = int(lengthofaccounts), size = len(mydates))
		Cheques = np.random.poisson(lam = int(lengthofcheques), size = len(mydates))
		General = np.random.poisson(lam = int(lengthofgeneral), size = len(mydates))

		df = pd.DataFrame(mydates)
		df = df.rename(columns={0: "Date"})
		df = pd.DataFrame(mydates)
		df = df.rename(columns={0: "Date"})
		df['Exchange'] = Exchange
		df['Loan'] = Loan
		df ['ATM'] = ATM
		df['Accounts'] = Accounts
		df['Cheques'] = Cheques
		df['General'] = General

		series = df[['Exchange']]
		X = difference(series.values)
		model = AR(X)
		model_fit = model.fit(maxlag=6, disp=False)
		predictions = model_fit.predict(start=len(X), end=len(X)+4, dynamic = True)
		obs = series['Exchange'].values.tolist()
		obs = obs[-5:]
		predictions = obs+predictions
		predictions = predictions.astype(int)
		preds = pd.DataFrame(predictions, columns = ['Exchange'])

		series = df[['Loan']]
		X = difference(series.values)
		model = AR(X)
		model_fit = model.fit(maxlag=6, disp=False)
		predictions = model_fit.predict(start=len(X), end=len(X)+4, dynamic = True)
		obs = series['Loan'].values.tolist()
		obs = obs[-5:]
		predictions = obs+predictions
		predictions = predictions.astype(int)
		preds['Loan'] = predictions

		series = df[['ATM']]
		X = difference(series.values)
		model = AR(X)
		model_fit = model.fit(maxlag=6, disp=False)
		predictions = model_fit.predict(start=len(X), end=len(X)+4, dynamic = True)
		obs = series['ATM'].values.tolist()
		obs = obs[-5:]
		predictions = obs+predictions
		predictions = predictions.astype(int)
		preds['ATM'] = predictions

		series = df[['Accounts']]
		X = difference(series.values)
		model = AR(X)
		model_fit = model.fit(maxlag=6, disp=False)
		predictions = model_fit.predict(start=len(X), end=len(X)+4, dynamic = True)
		obs = series['Accounts'].values.tolist()
		obs = obs[-5:]
		predictions = obs+predictions
		predictions = predictions.astype(int)
		preds['Accounts'] = predictions

		series = df[['Cheques']]
		X = difference(series.values)
		model = AR(X)
		model_fit = model.fit(maxlag=6, disp=False)
		predictions = model_fit.predict(start=len(X), end=len(X)+4, dynamic = True)
		obs = series['Cheques'].values.tolist()
		obs = obs[-5:]
		predictions = obs+predictions
		predictions = predictions.astype(int)
		preds['Cheques'] = predictions

		series = df[['General']]
		X = difference(series.values)
		model = AR(X)
		model_fit = model.fit(maxlag=6, disp=False)
		predictions = model_fit.predict(start=len(X), end=len(X)+4, dynamic = True)
		obs = series['General'].values.tolist()
		obs = obs[-5:]
		predictions = obs+predictions
		predictions = predictions.astype(int)
		preds['General'] = predictions

		exc_list = preds['Exchange'].to_list()
		lon_list = preds['Loan'].to_list()
		atm_list = preds['ATM'].to_list()
		acc_list = preds['Accounts'].to_list()
		chq_list = preds['Cheques'].to_list()
		gen_list = preds['General'].to_list()

		print(preds)
		res ={
			"Exchange": exc_list,
			"Loans": lon_list,
			"ATM": atm_list,
			"Accounts": acc_list,
			"Cheques": chq_list,
			"General": gen_list
		}

		return res, 200


"""
	endpoint '/show/timelogs' with GET statement for API.
	
	Gets all the enteries timestamp of all customers. returns the count of people in branch for particular hour in JSON format.
	
"""
@api.route('/show/timelogs', methods=['GET'])
class GetInfo(Resource):
	def get(self):
		conn = sqlite3.connect('data.db')
		cur = conn.cursor()
		cur.execute('select * from timelog')
		result = cur.fetchall()

		timelist = []
		cur.execute('select count(*) from timelog where time between "2020-04-19 22:00:00" AND "2020-04-19 23:00:00"')
		result = cur.fetchall()
		timecount8 = result[0][0]
		timelist.append(timecount8)
		cur.execute('select count(*) from timelog where time between "2020-04-19 23:00:00" AND "2020-04-19 00:00:00"')
		result = cur.fetchall()
		timecount9 = result[0][0]
		timelist.append(timecount9)
		cur.execute('select count(*) from timelog where time between "2020-04-19 00:00:00" AND "2020-04-19 01:00:00"')
		result = cur.fetchall()
		timecount10 = result[0][0]
		timelist.append(timecount10)
		cur.execute('select count(*) from timelog where time between "2020-04-19 01:00:00" AND "2020-04-19 02:00:00"')
		result = cur.fetchall()
		timecount11 = result[0][0]
		timelist.append(timecount11)
		cur.execute('select count(*) from timelog where time between "2020-04-19 02:00:00" AND "2020-04-19 03:00:00"')
		result = cur.fetchall()
		timecount12 = result[0][0]
		timelist.append(timecount12)
		cur.execute('select count(*) from timelog where time between "2020-04-19 03:00:00" AND "2020-04-19 04:00:00"')
		result = cur.fetchall()
		timecount13 = result[0][0]
		timelist.append(timecount13)
		cur.execute('select count(*) from timelog where time between "2020-04-19 04:00:00" AND "2020-04-19 05:00:00"')
		result = cur.fetchall()
		timecount14 = result[0][0]
		timelist.append(timecount14)
		cur.execute('select count(*) from timelog where time between "2020-04-19 05:00:00" AND "2020-04-19 06:00:00"')
		result = cur.fetchall()
		timecount15 = result[0][0]
		timelist.append(timecount15)
		cur.execute('select count(*) from timelog where time between "2020-04-19 06:00:00" AND "2020-04-19 07:00:00"')
		result = cur.fetchall()
		timecount16 = result[0][0]
		timelist.append(timecount16)
		
		conn.close()
		res={
			"time" : timelist
		}

		return res, 200

def difference(dataset):
	diff = list()
	for i in range(1, len(dataset)):
		value = dataset[i] - dataset[i - 1]
		diff.append(value)
	return np.array(diff)

def GenerateCustomerId():
	return randint(10000, 99999)

def GenerateTicket():
	return randint(100,999)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
