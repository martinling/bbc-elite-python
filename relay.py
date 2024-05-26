import zmq
import sys

ctx = zmq.Context()
game_socket = ctx.socket(zmq.PUB)
game_socket.bind('tcp://*:31337')

while True:
	ram = sys.stdin.buffer.read(0x10000)
	game_socket.send(ram)
