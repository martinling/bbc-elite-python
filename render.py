import sys
import numpy as np

while True:
	buf = sys.stdin.read(13*36)
	data = np.frombuffer(buf, dtype=np.uint8).reshape(13,36)
	for i, ship in enumerate(data):
		if np.all(ship == 0):
			continue
		pos = ship[0:9]
		rot = ship[9:27].view(dtype=np.int16).reshape(3,3)
		rest = ship[27:36]
		print "Ship ", i
		print "Position:", pos
		print "Rotation:"
		print rot
		print "State:", rest
