import numpy as np

data = np.fromfile("ship.dat", dtype=np.uint8)

class Ship(object):

	def __init__(self, data):
		header = data[:20]
		self.cargo_type = (header[0] & 0xF0) >> 4
		self.debris_pieces = (header[0] & 0xF)
		self.hitbox_area = header[1:3].view(np.uint16)[0]
		self.edge_offset = header[[3,16]].view(np.uint16)[0]
		self.face_offset = header[[4,17]].view(np.uint16)[0]
		self.heap_size = header[5]
		self.laser_vertex = header[6]
		self.num_vertices = header[8] / 6
		self.num_edges = header[9]
		self.bounty = header[10:12].view(np.uint16)[0]
		self.num_faces = header[12]
		self.dot_distance = header[13]
		self.max_energy = header[14]
		self.max_speed = header[15]
		self.scale_factor = header[18]

	def data_size(self):
		return (20 +
			6 * self.num_vertices +
			4 * self.num_edges +
			4 * self.num_faces)

offset = 0x1CD

while offset < len(data):
	ship = Ship(data[offset:])
	print ship.__dict__
	offset += ship.data_size()
