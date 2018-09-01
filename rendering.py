import numpy as np
from structures import *
from vtk import *

def normalise(vector):
	return vector / np.linalg.norm(vector)

def polygon_order(points, center, normal):
	if len(points) == 0:
		return np.array([])
	x = normalise(points[0] - center)
	z = normalise(normal)
	y = np.cross(x,z)
	px = np.dot(points, x)
	py = np.dot(points, y)
	return ConvexHull(np.array([px, py]).T).vertices

def ship_model(ship):
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
	polygons = vtkCellArray()
	for vertices, center, normal in zip(
			ship.face_vertices,
			ship.face_centers,
			ship.face_normals):
		order = polygon_order(ship.vertices[vertices], center, normal)
		if len(order) == 0:
			continue
		polygon = vtkPolygon()
		ids = polygon.GetPointIds()
		ids.SetNumberOfIds(len(order))
		for i, point in enumerate(vertices[order]):
			ids.SetId(i, point)
		polygons.InsertNextCell(polygon)
	model = vtkPolyData()
	model.SetPoints(points)
	model.SetLines(lines)
	model.SetPolys(polygons)
	return model

def ship_normals(ship):
	points = vtkPoints()
	points.SetNumberOfPoints(ship.num_faces * 2)
	lines = vtkCellArray()
	for vertices, center, normal in ship_faces(ship):
		points.SetPoint(2*i, center)
		points.SetPoint(2*i + 1, center + normal)
		line = vtkLine()
		line.GetPointIds().SetId(0, 2*i)
		line.GetPointIds().SetId(1, 2*i + 1)
		lines.InsertNextCell(line)
	model = vtkPolyData()
	model.SetLines(lines)
	return model

class ShipInstance(object):

	dummy = vtkPolyData()
	dummy.SetPoints(vtkPoints())

	sphere = vtkSphereSource()
	sphere.SetRadius(20000)
	sphere.SetPhiResolution(18)
	sphere.SetThetaResolution(36)

	def __init__(self, slot):
		self.slot = slot
		self.transform = vtkTransform()
		self.transform.PostMultiply()
		self.filter = vtkTransformPolyDataFilter()
		self.filter.SetTransform(self.transform)
		self.filter.SetInputData(self.dummy)
		self.mapper = vtkPolyDataMapper()
		self.mapper.SetInputConnection(self.filter.GetOutputPort())
		self.actor = vtkActor()
		prop = self.actor.GetProperty()
		prop.SetColor(0,0,0)
		prop.EdgeVisibilityOn()
		prop.SetEdgeColor(1,1,1)
		self.actor.SetMapper(self.mapper)
		self.actor.VisibilityOff()
		self.ship_type = 0

	def update(self, game):
		# Get ship type for this slot from game state.
		ship_type = game.ship_types[self.slot]

		if ship_type != self.ship_type:
			# Ship type has changed.
			if ship_type == 0:
				# Slot not in use.
				self.filter.SetInputData(self.dummy)
				self.actor.VisibilityOff()
			elif ship_type & 0x80:
				# Planet, render as a sphere.
				self.filter.SetInputConnection(self.sphere.GetOutputPort())
				self.actor.VisibilityOn()
			else:
				# Set correct model and make visible.
				self.ship = game.ship_data[ship_type - 1]
				self.filter.SetInputData(ship_model(self.ship))
				self.actor.VisibilityOn()
			self.ship_type = ship_type

		# Set transform from ship state.
		state = game.ship_states[self.slot]
		matrix = np.empty((4,4))
		matrix[0:3,0:3] = (state.rot[[2,1,0]] * np.array([-1, 1, 1])).T
		matrix[0:3,3] = state.pos * np.array([-1, 1, 1])
		matrix[3,0:3] = 0
		matrix[3,3] = 1
		self.transform.SetMatrix(matrix.reshape(16) / 200.0)
		self.filter.Update()

def lines_2d(points, lines):
	vpoints = vtkPoints()
	vpoints.SetNumberOfPoints(len(points))
	for i, (x, y) in enumerate(points):
		vpoints.SetPoint(i, x, y, 0)
	vlines = vtkCellArray()
	for start, end in lines:
		vline = vtkLine()
		vline.GetPointIds().SetId(0, start)
		vline.GetPointIds().SetId(1, end)
		vlines.InsertNextCell(vline)
	poly = vtkPolyData()
	poly.SetPoints(vpoints)
	poly.SetLines(vlines)
	coord = vtkCoordinate()
	coord.SetCoordinateSystemToNormalizedViewport()
	mapper = vtkPolyDataMapper2D()
	mapper.SetTransformCoordinate(coord)
	mapper.SetInputData(poly)
	mapper.Update()
	actor = vtkActor2D()
	actor.SetMapper(mapper)
	return actor

crosshair_points = np.array([
	[0.5, 0.55], [0.5, 0.6],
	[0.5, 0.45], [0.5, 0.4],
	[0.55, 0.5], [0.6, 0.5],
	[0.45, 0.5], [0.4, 0.5]])

crosshair_lines = np.array([
	[0, 1], [2, 3],
	[4, 5], [6, 7]])

border_points = np.array([
	[0.025, 0.025], [0.025, 0.975],
	[0.975, 0.975], [0.975, 0.025]])

border_lines = np.array([
	[0, 1], [1, 2],
	[2, 3], [3, 0]])
