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

def make_lines(points, lines):
	vpoints = vtkPoints()
	vpoints.SetNumberOfPoints(len(points))
	for i, point in enumerate(points):
		vpoints.SetPoint(i, point)
	vlines = vtkCellArray()
	for start, end in lines:
		vline = vtkLine()
		vline.GetPointIds().SetId(0, start)
		vline.GetPointIds().SetId(1, end)
		vlines.InsertNextCell(vline)
	poly = vtkPolyData()
	poly.SetPoints(vpoints)
	poly.SetLines(vlines)
	return poly

def ship_model(ship):
	model = make_lines(ship.vertices, ship.edges)
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
		self.prop = self.actor.GetProperty()
		self.prop.SetColor(0.4,0.4,0.4)
		self.prop.EdgeVisibilityOn()
		self.prop.SetEdgeColor(1,1,1)
		self.prop.SetLineWidth(3)
		self.actor.SetMapper(self.mapper)
		self.actor.VisibilityOff()
		self.ship_type = 0

	def update(self, game):
		# Get ship type and state for this slot from game state.
		ship_type = game.ship_types[self.slot]
		state = game.ship_states[self.slot]

		if ship_type != self.ship_type:
			# Ship type has changed.
			if ship_type == 0:
				# Slot not in use.
				self.filter.SetInputData(self.dummy)
				self.actor.VisibilityOff()
			elif ship_type & 0x80:
				# Planet, render as a sphere.
				self.filter.SetInputConnection(self.sphere.GetOutputPort())
				self.prop.EdgeVisibilityOff()
				self.actor.VisibilityOn()
			else:
				# Set correct model and make visible.
				self.ship = game.ship_data[ship_type - 1]
				self.filter.SetInputData(ship_model(self.ship))
				self.prop.EdgeVisibilityOn()
			self.ship_type = ship_type

		# Set transform from ship state.
		matrix = np.empty((4,4))
		matrix[0:3,0:3] = state.rot
		matrix[0:3,3] = state.pos
		matrix[3,0:3] = 0
		matrix[3,3] = 1
		self.transform.SetMatrix(matrix.reshape(16) / 50.0)
		self.filter.Update()

		# Set visibility according to whether ship is alive.
		self.actor.SetVisibility(state.is_alive())

def lines_2d(points, lines):
	points_3d = np.empty((len(points), 3))
	points_3d[:,0:2] = points
	points_3d[:,2] = 0
	poly = make_lines(points_3d, lines)
	coord = vtkCoordinate()
	coord.SetCoordinateSystemToNormalizedViewport()
	mapper = vtkPolyDataMapper2D()
	mapper.SetTransformCoordinate(coord)
	mapper.SetInputData(poly)
	actor = vtkActor2D()
	actor.SetMapper(mapper)
	return actor

def lines_3d(points_3d, lines):
	poly = make_lines(points_3d, lines)
	mapper = vtkPolyDataMapper()
	mapper.SetInputData(poly)
	actor = vtkActor()
	actor.SetMapper(mapper)
	return actor

def make_dust(game):
	points = vtkPoints()
	points.SetNumberOfPoints(game.num_dust * 2)
	lines = vtkCellArray()
	positions = (game.dust_positions) / 50.0
	speed = [0, 0, -game.speed / 200.0]
	for i, speck in enumerate(positions):
		points.SetPoint(2*i, speck)
		points.SetPoint(2*i+1, speck - speed)
		line = vtkLine()
		line.GetPointIds().SetId(0, 2*i)
		line.GetPointIds().SetId(1, 2*i+1)
		lines.InsertNextCell(line)
	poly = vtkPolyData()
	poly.SetPoints(points)
	poly.SetLines(lines)
	return poly

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

laser_points = np.array([
	[0.15, 0.00], [0.20, 0.00],
	[0.80, 0.00], [0.85, 0.00],
	[0.50, 0.50]
])

laser_lines = np.array([
	[0, 4], [1, 4],
	[2, 4], [3, 4]
])
