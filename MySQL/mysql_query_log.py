# -*- coding: utf-8 -*-
"""
@file Parser for mysql query log output.


"""


import fileinput
import pprint
import datetime


SESSION_OUTPUT_FILE = "mysql_session.txt"
LOGIN_OUTPUT_FILE = "mysql_connection.txt"


def insert_query(session_data,current_date, current_session_id, query):
	try:
		session_data[current_session_id][current_date].append(query)
	except KeyError:
		try:
			session_data[current_session_id][current_date] = [query]
		except KeyError:
			session_data[current_session_id]={current_date: [query]}
	return

def insert_connection(login_data, current_date, current_session_id, username, host, database):
	#try:
	#	login_data[username].add(host)
	#except KeyError:q
	#	login_data[username] = set([host,])
	#return

	try:
		login_data[username][current_session_id] = {'host':host, 'database': database, 'login_date': current_date}
	except KeyError:
		login_data[username] = {current_session_id: {'host': host, 'database': database, 'login_date': current_date}}
	return


def main():
	session_data = {}
	login_data = {}
	current_date = None
	current_query = ""
	current_action = ""
	current_session_id = ""
	for line in fileinput.input():
		#line = line.strip()
		parts = line.split("\t")
		parts = [part.strip() for part in parts]

		length = len(parts)

		if length in [4,3]:
			if current_query:
				#insert_query(session_data, current_date, current_session_id,  current_query)
				current_query = ""

			if length == 3:
				current_date, session_id_and_action, data = parts
				current_session_id,current_action = session_id_and_action.split(" ")
				current_date = datetime.datetime.strptime(current_date,"%y%m%d %H:%M:%S").isoformat()
			elif length == 4:
				_,_, session_id_and_action, data = parts

				try:
					current_session_id,current_action = session_id_and_action.split(" ")
				except ValueError:
					print session_id_and_action.__repr__()
					print parts
					raise

			if current_action == "Query":
				current_query += data
			elif current_action == "Connect":
				this_data = data.split(" ")
				username, host = this_data[0].split("@")
				if len(this_data) == 2:
					database = None
				else:
					database = this_data[-1]
				insert_connection(login_data, current_date, current_session_id, username, host, database)
		else:
			current_query += "\t".join(parts) + "\n"


	print "Storing data..."

	with open(SESSION_OUTPUT_FILE,"w") as f:
		pprint.pprint(session_data, stream = f)
	with open(LOGIN_OUTPUT_FILE, "w") as f:
		pprint.pprint(login_data, stream = f)
	return



if __name__ == "__main__":
	main()