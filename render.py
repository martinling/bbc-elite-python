import sys
import numpy as np

def int24(b):
	magnitude = (b[2] & 0x7F) << 16 | b[1] << 8 | b[0]
	sign = -1 if b[2] & 0x80 else 1
	return sign * magnitude

while True:
	buf = sys.stdin.read(13*36)
	data = np.frombuffer(buf, dtype=np.uint8).reshape(13,36)
	for i, ship in enumerate(data):
		if np.all(ship == 0):
			continue
		pos = map(int24, ship[0:9].reshape(3, 3))
		rot = ship[9:27].view(dtype=np.int16).reshape(3,3)
		rest = ship[27:36]
		print "Ship ", i
		print "Position:", pos
		print "Rotation:"
		print rot
		print "State:", rest
