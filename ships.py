import numpy as np
from vtk import *

data = np.fromfile("ship.dat", dtype=np.uint8)

def vertices(b):
	magnitudes = b[:,0:3]
	signs = b[:,3:4] & [0x80, 0x40, 0x20]
	return magnitudes * np.where(signs, -1.0, 1.0)

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
		data = data[header.nbytes:]
		vertex_data = data[:6*self.num_vertices].reshape(-1,6)
		data = data[vertex_data.nbytes:]
		edge_data = data[:4*self.num_edges].reshape(-1,4)
		data = data[edge_data.nbytes:]
		face_data = data[:4*self.num_faces].reshape(-1,4)
		self.vertices = vertices(vertex_data)
		self.edges = edge_data[:,2:4] / 4

	def data_size(self):
		return (20 +
			6 * self.num_vertices +
			4 * self.num_edges +
			4 * self.num_faces)

offset = 0x1CD

ship = Ship(data[offset:])
offset += ship.data_size()
print ship.__dict__
points = vtkPoints()
points.SetNumberOfPoints(ship.num_vertices)
for i, vertex in enumerate(ship.vertices):
	points.SetPoint(i, vertex)
lines = vtkCellArray()
for edge in ship.edges:
	line = vtkLine()
	for i, vertex_id in enumerate(edge):
		line.GetPointIds().SetId(i, vertex_id)
	lines.InsertNextCell(line)
poly = vtkPolyData()
poly.SetPoints(points)
poly.SetLines(lines)
mapper = vtkPolyDataMapper()
mapper.SetInputData(poly)
actor = vtkActor()
actor.SetMapper(mapper)
renderer = vtkRenderer()
renderer.AddActor(actor)
window = vtkRenderWindow()
window.AddRenderer(renderer)
interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.Start()
