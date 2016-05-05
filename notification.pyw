import sqlite3
from tkinter import * 
import time
conn = sqlite3.connect('database.db')
c = conn.cursor()
class App:
	"""Displays a notification in a window"""
	def __init__(self, arg):
		c.execute('SELECT name, bday FROM friends')
		dates = c.fetchall()
		currentDay = time.strftime("%d")
		currentMonth = time.strftime("%m")
		hasBirthday = ['']
		for date in dates:
			x = date[1].split('.')
			if None not in x and "None" not in x:
				day = x[0]
				month = x[1]
				if day == currentDay and month == currentMonth:
					hasBirthday.append(date[0])
		if hasBirthday != ['']:
			self.arg = arg
			string = ""
			for person in hasBirthday:
				string += person + '\n'
			t = Label(arg, text=u"Dneska má narozeniny:", fg="red", font=("Arial", 20), justify=LEFT)
			t.pack()
			p = Label(arg, text=string, font=("Arial", 16), justify=LEFT)
			p.pack()
		else: exit()
root = Tk()
app = App(root)
root.title("Notification")
root.mainloop()
c.close()
conn.close()