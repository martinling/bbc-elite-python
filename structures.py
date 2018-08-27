import numpy as np
from vtk import *

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
		self.num_vertices = header[8] / 6
		self.num_edges = header[9]
		self.bounty = header[10:12].view(np.uint16)[0]
		self.num_faces = header[12] / 4
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
		self.vertices = vertices(vertex_data)
		self.vertex_faces = nibbles(vertex_data[:,4:6])
		self.edges = edge_data[:,2:4] / 4
		self.edge_faces = nibbles(edge_data[:,1:2])
		self.normals = normals(face_data)
		if np.any(self.edges >= self.num_vertices):
			raise ValueError
		points = vtkPoints()
		points.SetNumberOfPoints(self.num_vertices + self.num_faces * 2)
		for i, vertex in enumerate(self.vertices):
			points.SetPoint(i, vertex)
		lines = vtkCellArray()
		for edge in self.edges:
			line = vtkLine()
			for i, vertex_id in enumerate(edge):
				line.GetPointIds().SetId(i, vertex_id)
			lines.InsertNextCell(line)
		polygons = vtkCellArray()
		for i in range(self.num_faces):
			face_vertices = np.unique([
				v for v in range(self.num_vertices)
					if v in self.vertex_faces[v]])
			face_edges = np.array([self.edges[e]
				for e in range(self.num_edges)
				if i in self.edge_faces[e]])
			face_edge_ends = np.unique(face_edges.flatten())
			face_points = face_edge_ends
			face_center = np.mean(self.vertices[face_points], axis=0)
			a = self.num_vertices + 2*i
			b = a + 1
			points.SetPoint(a, face_center)
			points.SetPoint(b, face_center + self.normals[i])
			line = vtkLine()
			line.GetPointIds().SetId(0, a)
			line.GetPointIds().SetId(1, b)
			lines.InsertNextCell(line)
			polygon = vtkPolygon()
			ids = polygon.GetPointIds()
			ids.SetNumberOfIds(len(face_points))
			for k, point in enumerate(face_points):
				ids.SetId(k, point)
			polygons.InsertNextCell(polygon)
		self.poly = vtkPolyData()
		self.poly.SetPoints(points)
		self.poly.SetLines(lines)
		self.poly.SetPolys(polygons)

class ShipState(object):

	def __init__(self, state):
		self.pos = int24(state[0:9])
		self.rot = int16(state[9:27]).reshape(3,3) / float(0x6000)
		self.rest = state[27:37]

class Game(object):

	def __init__(self):
		self.ship_data = [None] * 31
		self.ship_types = [None] * 13
		self.ship_states = [None] * 13

	def update(self, ram):
		# Get addresses where ship data is loaded
		self.ship_addrs = ram[0x5600:0x5600+64].view(np.uint16)

		# Read data for any ships we don't already know
		for i, addr in enumerate(self.ship_addrs):
			if addr == 0:
				# Ship type not currently loaded
				continue
			elif self.ship_data[i]:
				# Already read this ship type
				continue
			else:
				# Read this ship type
				try:
					self.ship_data[i] = ShipData(ram, addr)
				except ValueError:
					pass

		# Read ship states
		self.ship_states = [ShipState(state)
			for state in ram[0x900:0x900 + 13*37].reshape(13,37)]

		# Read ship types
		self.ship_types = ram[0x311:0x311 + 13]
