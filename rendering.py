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

def ship_model(ship):
	points = vtkPoints()
	points.SetNumberOfPoints(ship.num_vertices + ship.num_faces * 2)
	for i, vertex in enumerate(ship.vertices):
		points.SetPoint(i, vertex)
	lines = vtkCellArray()
	for edge in ship.edges:
		line = vtkLine()
		for i, vertex_id in enumerate(edge):
			line.GetPointIds().SetId(i, vertex_id)
		lines.InsertNextCell(line)
	polygons = vtkCellArray()
	for i in range(ship.num_faces):
		face_edges = np.any(ship.edge_faces == i, axis=1)
		face_points = np.unique(ship.edges[face_edges].flatten())
		face_center = np.mean(ship.vertices[face_points], axis=0)
		face_normal = ship.normals[i]
		face_order = polygon_order(ship.vertices[face_points], face_center, face_normal)
		a = ship.num_vertices + 2*i
		b = a + 1
		points.SetPoint(a, face_center)
		points.SetPoint(b, face_center + face_normal)
		line = vtkLine()
		line.GetPointIds().SetId(0, a)
		line.GetPointIds().SetId(1, b)
		lines.InsertNextCell(line)
		polygon = vtkPolygon()
		ids = polygon.GetPointIds()
		ids.SetNumberOfIds(len(face_order))
		for k, point in enumerate(face_points[face_order]):
			ids.SetId(k, point)
		polygons.InsertNextCell(polygon)
	model = vtkPolyData()
	model.SetPoints(points)
	model.SetLines(lines)
	model.SetPolys(polygons)
	return model
