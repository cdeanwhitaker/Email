#!/usr/bin/python
import socket, ssl
from ConfigParser import ConfigParser as config

class MailClientConnection:
	def __init__ (self):
		self.readConfig()
		try:
			data = "connecting"
			self.ssl_sock = self.connect ((self.fqdn, self.imaps))
			data = self.ssl_sock.recv (1024)
			self.ssl_sock.send (". LOGIN %s %s\n" % (self.account, self.password))
			data = self.ssl_sock.recv (1024)
			self.ssl_sock.send (". LIST '' '*'\n")
			data = self.ssl_sock.recv (1024)
		except Exception as e:
			print "ERROR"
			print data
			print str (e)

	def __del__ (self):
		self.ssl_sock.send (". LOGOUT\n")

	def readConfig (self):
		cfg = config()
		cfg.read ("mailclient.cfg")
		self.fqdn = cfg.get ("mailhost", "fqdn")
		self.imaps = int (cfg.get ("mailhost", "imaps"))
		self.account = cfg.get ("mailbox", "account")
		self.password = cfg.get ("mailbox", "password")
		self.ssl_cert = cfg.get ("ssl", "cert")

	def fetchSize (self):
		mailboxSize = 0
		self.ssl_sock.send (". EXAMINE INBOX\n")
		output = ""
		data = self.ssl_sock.recv (1)
		while "Select completed" not in output:
			data = self.ssl_sock.recv (1)
			output = output + data
		for l in output.split ("\n"):
			if "EXISTS" in l:
				dummy, num, exists = l.split (" ")
				mailboxSize = int (num)
		return mailboxSize

	def fetchMsgSubject (self, msgNum):
		self.ssl_sock.send (". FETCH %d BODY[HEADER]\n" % msgNum)
		output = ""
		data = self.ssl_sock.recv (1)
		while "Fetch completed" not in output:
			data = self.ssl_sock.recv (1)
			output = output + data
		subject = ""
		body = ""
		for l in output.split ("\n"):
			if "Subject:" in l:
				dummy, subject = l.split (": ")
		return subject

	def fetchMsgBody (self, msgNum):
		self.ssl_sock.send (". FETCH %d BODY[TEXT]\n" % msgNum)
		output = ""
		data = self.ssl_sock.recv (1)
		while "Fetch completed" not in output:
			data = self.ssl_sock.recv (1)
			output = output + data
		body = ""
		for l in output.split ("\r"):
			if "FETCH (BODY[TEXT]" not in l:
				if "Fetch completed" not in l:
					body = body + l
		return body

	def connect (self, hostTuple):
		print "Connecting to",
		print hostTuple
		s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
		ssl_sock = ssl.wrap_socket (s, ca_certs=self.ssl_cert, cert_reqs=ssl.CERT_REQUIRED)
		ssl_sock.connect (hostTuple)
		return ssl_sock


mc = MailClientConnection()
num = mc.fetchSize()
for i in xrange (1,num):
	print mc.fetchMsgSubject (i)
print mc.fetchMsgBody (num)
