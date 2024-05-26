import socket
import numpy as np

class Client(object):

	def __init__(self, sock):
		self.sock = sock

	def update(self):
		# Read RAM from emulator
		size = 0x10000
		received = 0
		data = bytes()
		while received < size:
			block = self.sock.recv(size - received)
			data += block
			received += len(block)
		return np.frombuffer(data, dtype=np.uint8)

class Server(object):

	def __init__(self, address="0.0.0.0", port=31337):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.settimeout(None)
		self.sock.bind((address, port))
		self.sock.listen(1)


	def accept(self):
		sock, addr = self.sock.accept()
		return Client(sock)
