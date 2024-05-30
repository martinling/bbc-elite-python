import zmq
import sys
import subprocess

ctx = zmq.Context()
game_socket = ctx.socket(zmq.PUB)
game_socket.bind('tcp://*:31337')

emulator = subprocess.Popen(
	["./b-em/b-em", "-disc", "elite.ssd"] + sys.argv[1:],
	stdout=subprocess.PIPE)

while True:
	ram = emulator.stdout.read(0x10000)
	game_socket.send(ram)
