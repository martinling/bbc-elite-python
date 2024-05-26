from select import select
import socket
import numpy as np

class Client(object):

	def __init__(self, sock):
		self.sock = sock
		sock.setblocking(False)
		self.size = 0x10000
		self.data = np.empty(self.size, dtype=np.uint8)
		self.received = 0

	def update_nonblocking(self):
		try:
			length = self.sock.recv_into(self.data[self.received:])
		except BlockingIOError:
			return None
		if length == 0:
			return None
		self.received += length
		if self.received == self.size:
			self.received = 0
			return self.data
		else:
			return None

	def update_blocking(self):
		while True:
			readable, _, _ = select([self.sock], [], [])
			if (ram := self.update_nonblocking()) is not None:
				return ram

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
