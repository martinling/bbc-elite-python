import numpy as np
import zmq
import config

ctx = zmq.Context()

class Source(object):

	def __init__(self):
		self.sock = ctx.socket(zmq.SUB)
		self.sock.connect(f"tcp://{config.server}:31337")
		self.sock.subscribe('')

	def update_nonblocking(self):
		try:
			return np.frombuffer(self.sock.recv(zmq.NOBLOCK), dtype=np.uint8)
		except zmq.ZMQError:
			return None

	def update_blocking(self):
		return np.frombuffer(self.sock.recv(), dtype=np.uint8)
