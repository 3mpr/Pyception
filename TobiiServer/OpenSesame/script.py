import socket
import os
import json
import threading
import csv

class TobiiLogger:

	LOCAL_IP = "127.0.0.1"
	LOCAL_PORT = 4527

	def __init__( self, ip = None, port = None ):

		self.connected = False

		self.ip = ip if ip is not None else self.LOCAL_IP
		self.port = port if port is not None else self.LOCAL_PORT

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.parser = json.JSONDecoder();

		self.field_names = ['Timestamp', 'X', 'Y']
		self.csv_path = os.path.join( var.experiment_path, 'subjects' )
		self.csv_path = os.path.join( self.csv_path, ('tobii-subject-%d.csv' % var.subject_nr) );

	def __del__( self ):

		self.sock.close()

	def bootstrap( self ):

		print( "Preparing CSV file at %s..." % self.csv_path )

		csv_file = open( self.csv_path, 'w+' )
		csv_file.write( "sep=,\r\n" )
		csv_file.close()

		print( "Done.\n" )

		print( "Attempting to subscribe to TobiiLogger at %s:%d..." % (self.ip, self.port) )
		self.sock.sendto( "subscribe", (self.ip, self.port) )

		try:

			data = self.sock.recv(1048)
			if(data == "OK"):
				self.connected = True

		except socket.timeout:

			raise socket.timeout( "Unable to contact local TobiiLogger Server" )

		if self.connected:

			print( "Done.\n" )

	def listen( self ):

		with open(self.csv_path, 'a') as csvfile:

			writer = csv.DictWriter(csvfile, fieldnames = self.field_names, dialect = 'excel', lineterminator = '\n')
			writer.writeheader()
			while self.connected:

				data = self.sock.recv(1048)
				coord = self.parser.decode(data)

				writer.writerow({'Timestamp': coord['Timestamp'], 'X': unicode(coord['X']), 'Y': unicode(coord['Y'])})

		self.sock.sendto("close", ("127.0.0.1", 4527))
		self.sock.close()



print( "Starting experiment " + var.title + " for subject " + str(var.subject_nr) + "." )

tobii_logger = TobiiLogger()
tobii_logger.bootstrap()
t_tobii = threading.Thread(target = tobii_logger.listen)
