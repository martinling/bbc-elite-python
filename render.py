import sys
import numpy as np

def int24(x):
	b = x.reshape(-1, 3).astype(np.uint32)
	magnitude = (b[:,2] & 0x7F) << 16 | b[:,1] << 8 | b[:,0]
	sign = np.where(b[:,2] & 0x80, -1, 1)
	return sign * magnitude

def int16(x):
	b = x.reshape(-1, 2).astype(np.uint32)
	magnitude = (b[:,1] & 0x7F) << 8 | b[:,0]
	sign = np.where(b[:,1] & 0x80, -1, 1)
	return sign * magnitude

while True:
	buf = sys.stdin.read(13*36)
	data = np.frombuffer(buf, dtype=np.uint8).reshape(13,36)
	for i, ship in enumerate(data):
		if np.all(ship == 0):
			continue
		pos = int24(ship[0:9])
		rot = int16(ship[9:27]).reshape(3,3) / float(0x6000)
		rest = ship[27:36]
		print "Ship ", i
		print "Position:", pos
		print "Rotation:"
		print rot
		print "State:", rest
