import numpy as np
from vtk import *

def vertices(b):
	magnitudes = b[:,0:3]
	signs = b[:,3:4] & [0x80, 0x40, 0x20]
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
		data = data[header.nbytes:]
		vertex_data = data[:6*self.num_vertices].reshape(-1,6)
		data = data[vertex_data.nbytes:]
		edge_data = data[:4*self.num_edges].reshape(-1,4)
		data = data[edge_data.nbytes:]
		face_data = data[:4*self.num_faces].reshape(-1,4)
		self.vertices = vertices(vertex_data)
		self.edges = edge_data[:,2:4] / 4
		if np.any(self.edges >= self.num_vertices):
			raise ValueError
		points = vtkPoints()
		points.SetNumberOfPoints(self.num_vertices)
		for i, vertex in enumerate(self.vertices):
			points.SetPoint(i, vertex / 200.0)
		lines = vtkCellArray()
		for edge in self.edges:
			line = vtkLine()
			for i, vertex_id in enumerate(edge):
				line.GetPointIds().SetId(i, vertex_id)
			lines.InsertNextCell(line)
		self.poly = vtkPolyData()
		self.poly.SetPoints(points)
		self.poly.SetLines(lines)
