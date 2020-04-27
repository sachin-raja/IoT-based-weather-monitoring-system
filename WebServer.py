from flask import Flask, render_template, request
app = Flask(__name__)

import time
import sqlite3
import Adafruit_DHT
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
source="one.1993.player@gmail.com"
destination="sraja5@hawk.iit.edu"

def moniter():
	msg = MIMEMultipart()
	msg['From'] = source
	msg['To'] = destination
	msg['Subject'] = "ECE442 - Weather Alert"
	body = 'Abnormal Temperature! Please, maintain your temperature'
	msg.attach(MIMEText(body, 'plain'))
	
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo
	server.starttls()
	server.login(source, "ece442project")
	text = msg.as_string()
	server.sendmail(source, destination, text)
	server.quit()

dbname='sensorsData.db'
def getDHTdata():	
	DHT22Sensor = Adafruit_DHT.DHT22
	DHTpin = 16
	hum, temp = Adafruit_DHT.read_retry(DHT22Sensor, DHTpin)
	
	if hum is not None and temp is not None:
		hum = round(hum)
		temp = round(temp, 1)
		logData (temp, hum)

# log sensor data on database
def logData (temp, hum):	
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()

	curs.execute("INSERT INTO DHT_data values(datetime('now','localtime'), (?), (?))", (temp, hum))
	conn.commit()
	conn.close()

# Retrieve data from database
def getData():
	conn=sqlite3.connect('/home/pi/WMSPro/server/sensorsData.db')
	curs=conn.cursor()

	for row in curs.execute("SELECT * FROM DHT_data ORDER BY temp desc LIMIT 1"):
		time = str(row[0])
		temp = row[1]
		if temp > 30:
			moniter()	
		hum = row[2]
	conn.close()
	return time, temp, hum

# main route 
@app.route("/")
def index():
	getDHTdata()	
	time, temp, hum = getData()
	templateData = {
		'time': time,
		'temp': temp,
		'hum': hum
	}
	return render_template('index.html', **templateData)

if __name__ == "__main__":
   app.run(debug=True, host='0.0.0.0', port=80)

from flask import Flask
