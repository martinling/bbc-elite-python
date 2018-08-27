import numpy as np
from scipy.spatial import ConvexHull
from vtk import *

def polygon_order(points, center, normal):
	x = points[0] - center
	x /= np.linalg.norm(x)
	z = normal / np.linalg.norm(normal)
	y = np.cross(x,z)
	px = np.dot(points, x)
	py = np.dot(points, y)
	p2d = np.array([px, py]).T
	return ConvexHull(np.array([px, py]).T).vertices

def ship_faces(ship):
	for i in range(ship.num_faces):
		edges = np.any(ship.edge_faces == i, axis=1)
		vertices = np.unique(ship.edges[edges].flatten())
		center = np.mean(ship.vertices[vertices], axis=0)
		normal = ship.normals[i]
		yield vertices, center, normal

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
	for vertices, center, normal in ship_faces(ship):
		order = polygon_order(ship.vertices[vertices], center, normal)
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