from firebase import Firebase
import json
import time
import os

config = {
  "apiKey": "AIzaSyDknQH4s32saqnDrb0S1wlz6mAdFUTB23U",
  "authDomain": "testproject-a2467.firebaseapp.com",
  "databaseURL": "https://testproject-a2467.firebaseio.com",
  "storageBucket": "testproject-a2467.appspot.com"
}

firebase = Firebase(config)

fdb = firebase.database()
oldLastModified = os.stat('database.json')[8]

while True:
	with open('database.json') as f:
		data = json.load(f)
		newLastModified = os.stat('database.json')[8]

	if (oldLastModified == newLastModified):
		print("File same...not sending any new data...")

	else:
		fdb.child('database').update(data)
		print("Send data...")

	oldLastModified = newLastModified
	time.sleep(1)



