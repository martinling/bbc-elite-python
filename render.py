import sys
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

def vertices(b):
	magnitudes = b[:,0:3]
	signs = b[:,3:4] & [0x80, 0x40, 0x20]
	return magnitudes * np.where(signs, -1.0, 1.0)

class Ship(object):

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
			raise IndexError
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

	def __repr__(self):
		return "Ship<0x%04X>" % self.addr

ram = np.frombuffer(sys.stdin.read(0x10000), dtype=np.uint8)
offsets = ram[0x5600:0x5600+64].view(np.uint16)
ships = [None] * 32

for i, offset in enumerate(offsets):
	if offset != 0:
		try:
			ships[i] = Ship(ram, offset)
		except IndexError:
			pass

camera = vtkCamera()
camera.SetPosition(0, 0, 0)
camera.SetFocalPoint(0, 0, 100)
renderer = vtkRenderer()
renderer.SetActiveCamera(camera)
window = vtkRenderWindow()
window.AddRenderer(renderer)
cube = vtkCubeSource()

transforms = [None] * 13
filters = [None] * 13

while True:
	ram = np.frombuffer(sys.stdin.read(0x10000), dtype=np.uint8)
	data = ram[0x900:0x900 + 13*37].reshape(13,37)
	types = ram[0x311:0x311 + 13]
	for i in range(13):
		if types[i] == 0x80:
			# planet
			continue
		if types[i] == 0:
			continue
		state = data[i]
		if np.all(state == 0):
			continue
		ship = ships[types[i] - 1]
		pos = int24(state[0:9])
		rot = int16(state[9:27]).reshape(3,3) / float(0x6000)
		rest = state[27:37]
		print "Ship ", i
		print "Position:", pos
		print "Rotation:"
		print rot
		print "State:", str.join(" ", ["%02X" % b for b in rest])
		if not transforms[i]:
			transforms[i] = vtkTransform()
			transforms[i].PostMultiply()
			filters[i] = vtkTransformPolyDataFilter()
			if ship:
				filters[i].SetInputData(ship.poly)
			else:
				filters[i].SetInputConnection(cube.GetOutputPort())
			filters[i].SetTransform(transforms[i])
			mapper = vtkPolyDataMapper()
			mapper.SetInputConnection(filters[i].GetOutputPort())
			actor = vtkActor()
			actor.SetMapper(mapper)
			renderer.AddActor(actor)
		matrix = np.empty((4,4))
		matrix[0:3,0:3] = (rot[[2,1,0]] * np.array([-1, 1, 1])).T
		matrix[0:3,3] = pos * np.array([-1, 1, 1]) / 200.0
		matrix[3,0:3] = 0
		matrix[3,3] = 1
		transforms[i].SetMatrix(matrix.reshape(16))
		filters[i].Update()
	print types
	print map(hex, offsets)
	print ships
	window.Render()
