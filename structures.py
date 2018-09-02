import numpy as np
from scipy.spatial import ConvexHull

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

def int8(x):
	magnitude = x & 0x7F
	sign = np.where(x & 0x80, -1, 1)
	return sign * magnitude

def nibbles(b):
	shape = list(b.shape)
	shape[-1] *= 2
	result = np.empty(shape, dtype=np.uint8)
	result[:,0::2] = b >> 4
	result[:,1::2] = b & 0xF
	return result

def vertices(b):
	magnitudes = b[:,0:3]
	signs = b[:,3:4] & [0x80, 0x40, 0x20]
	return magnitudes * np.where(signs, -1.0, 1.0)

def normals(b):
	magnitudes = b[:,1:4]
	signs = b[:,0:1] & [0x80, 0x40, 0x20]
	return magnitudes * np.where(signs, -1.0, 1.0)

def normalise(vector):
	return vector / np.linalg.norm(vector)

class ShipData(object):

	def __init__(self, ram, addr):
		self.addr = addr
		data = ram[addr:]
		header = data[:20]
		self.cargo_type = (header[0] & 0xF0) >> 4
		self.debris_pieces = (header[0] & 0xF)
		self.hitbox_area = header[1:3].view(np.uint16)[0]
		self.edge_offset = header[[3,16]].view(np.uint16)[0]
		self.face_offset = header[[4,17]].view(np.uint16)[0]
		self.heap_size = header[5]
		self.laser_vertex = header[6]
		self.num_vertices = header[8] // 6
		self.num_edges = header[9]
		self.bounty = header[10:12].view(np.uint16)[0]
		self.num_faces = header[12] // 4
		self.dot_distance = header[13]
		self.max_energy = header[14]
		self.max_speed = header[15]
		self.scale_factor = header[18]
		self.laser_power = header[19] >> 3
		self.missiles = header[19] & 0x07
		data = data[header.nbytes:]
		vertex_data = data[:6*self.num_vertices].reshape(-1,6)
		data = data[vertex_data.nbytes:]
		edge_data = data[:4*self.num_edges].reshape(-1,4)
		data = data[edge_data.nbytes:]
		face_data = data[:4*self.num_faces].reshape(-1,4)
		self.vertices = vertices(vertex_data)[:,::-1] * [1, 1, -1]
		self.vertex_faces = nibbles(vertex_data[:,4:6])
		self.edges = edge_data[:,2:4] // 4
		if np.any(self.edges >= self.num_vertices):
			raise ValueError
		self.edge_faces = nibbles(edge_data[:,1:2])
		self.face_normals = normals(face_data)[:,::-1] * [1, 1, -1]
		self.face_centers = np.empty((self.num_faces, 3))[:,::-1] * [1, 1, -1]
		self.face_vertices = []
		for i in range(self.num_faces):
			normal = normalise(self.face_normals[i])
			edges = np.nonzero(np.any(self.edge_faces == i, axis=1))[0]
			if len(edges) > 3:
				edge_vectors = np.diff(
					self.vertices[self.edges[edges]], axis=1)[:,0]
				plane_error = np.array([
					np.abs(np.dot(normal, normalise(e)))
						for e in edge_vectors])
				edges = edges[plane_error < 0.1]
			self.face_vertices.append(np.unique(self.edges[edges].flatten()))
			self.face_centers[i] = np.mean(self.vertices[self.face_vertices[i]], axis=0)

class ShipState(object):

	def __init__(self, state):
		self.pos = int24(state[0:9]) * [1,1,-1]
		self.rot = (int16(state[9:27]).reshape(3,3) / float(0x6000) * [1,1,-1]).T
		self.speed = state[27]
		self.accel = state[28]
		self.roll = state[29]
		self.pitch = state[30]
		self.visibility = state[31]
		self.attack = state[32]
		self.heap = state[33:35].view(np.uint16)
		self.energy = state[35]
		self.behaviour = state[36]

class Game(object):

	def __init__(self):
		self.ship_data = [None] * 31
		self.ship_types = [None] * 13
		self.ship_states = [None] * 13
		self.num_dust = None
		self.dust_positions = None

	def update(self, ram):
		# Get addresses where ship data is loaded
		self.ship_addrs = ram[0x5600:0x5600+64].view(np.uint16)

		# Read ship types. Check if a new space station has spawned.
		ship_types = ram[0x311:0x311 + 13]
		new_station = (2 in ship_types) and not (2 in self.ship_types)
		self.ship_types = ship_types

		# Read data for any ships we don't already know
		for i, addr in enumerate(self.ship_addrs):
			if addr == 0:
				# Ship type not currently loaded
				continue
			elif self.ship_data[i]:
				if i == 1 and new_station:
					# Space station, two versions of model.
					pass
				else:
					# Already read this ship type
					continue
			# Read this ship type
			try:
				self.ship_data[i] = ShipData(ram, addr)
			except ValueError:
				pass

		# Read ship states
		self.ship_states = [ShipState(state)
			for state in ram[0x900:0x900 + 13*37].reshape(13,37)]

		# Read dust count and positions
		self.num_dust = ram[0x3C3]
		self.dust_positions = np.empty((self.num_dust, 3))
		self.dust_positions[:,0] = int8(ram[0xF5D:0xF5D+self.num_dust])
		self.dust_positions[:,1] = int8(ram[0xF83:0xF83+self.num_dust])
		self.dust_positions[:,2] = -ram[0xFA9:0xFA9+self.num_dust].astype(int)

		# Read player speed
		self.speed = int(ram[0x7D])

		# Read laser key
		self.laser_firing = bool(ram[0x307])

		# Read pitch and roll
		self.roll_rate = int8(ram[0x8D])
		self.pitch_rate = int8(ram[0x2A])
