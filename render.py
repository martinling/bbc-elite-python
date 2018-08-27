import sys
import numpy as np
from vtk import *
from structures import *

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
ships = [None] * 32

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.read(0x10000), dtype=np.uint8)

	# Get addresses where ship data is loaded
	offsets = ram[0x5600:0x5600+64].view(np.uint16)

	# Read data for any ships we don't already know
	for i, offset in enumerate(offsets):
		if offset == 0:
			# Ship type not currently loaded
			continue
		elif ships[i]:
			# Already read this ship type
			continue
		else:
			# Read this ship type
			try:
				ships[i] = ShipData(ram, offset)
			except ValueError:
				pass

	# Read ship states
	states = ram[0x900:0x900 + 13*37].reshape(13,37)

	# Read ship types
	types = ram[0x311:0x311 + 13]

	for i in range(13):
		if types[i] == 0:
			# This ship slot not in use.
			continue
		if types[i] & 0x80:
			# Planet - not a wireframe, needs special handling.
			continue
		state = states[i]
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
	window.Render()
