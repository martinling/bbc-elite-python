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

shipdata = sys.stdin.read(0xA51)
open("ship.dat", 'wb').write(shipdata)

source = vtkCubeSource()
camera = vtkCamera()
camera.SetPosition(0, 0, 0)
camera.SetFocalPoint(0, 0, 100)
renderer = vtkRenderer()
renderer.SetActiveCamera(camera)
window = vtkRenderWindow()
window.AddRenderer(renderer)

transforms = [None] * 13
filters = [None] * 13

while True:
	buf = sys.stdin.read(13*37)
	data = np.frombuffer(buf, dtype=np.uint8).reshape(13,37)
	for i, ship in enumerate(data[1:]):
		if np.all(ship == 0):
			continue
		pos = int24(ship[0:9])
		rot = int16(ship[9:27]).reshape(3,3) / float(0x6000)
		rest = ship[27:37]
		print "Ship ", i
		print "Position:", pos
		print "Rotation:"
		print rot
		if not transforms[i]:
			transforms[i] = vtkTransform()
			transforms[i].PostMultiply()
			filters[i] = vtkTransformPolyDataFilter()
			filters[i].SetInputConnection(source.GetOutputPort())
			filters[i].SetTransform(transforms[i])
			mapper = vtkPolyDataMapper()
			mapper.SetInputConnection(filters[i].GetOutputPort())
			actor = vtkActor()
			actor.SetMapper(mapper)
			renderer.AddActor(actor)
		matrix = np.empty((4,4))
		matrix[0:3,0:3] = (rot * np.array([-1, 1, 1])).T
		matrix[0:3,3] = pos * np.array([-1, 1, 1]) / float(200)
		matrix[3,0:3] = 0
		matrix[3,3] = 1
		transforms[i].SetMatrix(matrix.reshape(16))
		filters[i].Update()
	window.Render()
