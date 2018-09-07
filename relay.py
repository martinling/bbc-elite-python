import sys, socket

sock = socket.create_connection((sys.argv[1], 31337))
sock.settimeout(None)

while True:
	ram = sys.stdin.buffer.read(0x10000)
	sock.sendall(ram)
