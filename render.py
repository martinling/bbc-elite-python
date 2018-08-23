import sys
import numpy as np

while True:
	buf = sys.stdin.read(13*36)
	data = np.frombuffer(buf, dtype=np.uint8).reshape((13,36))
	print data
