import sys
import numpy as np
from vtk import *
from structures import *
from rendering import *

camera = vtkCamera()
camera.SetPosition(0, 0, 0)
camera.SetFocalPoint(0, 0, 100)
renderer = vtkRenderer()
renderer.SetActiveCamera(camera)
window = vtkRenderWindow()
window.AddRenderer(renderer)

transforms = [None] * 13
filters = [None] * 13

game = Game()

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.read(0x10000), dtype=np.uint8)

	# Update game state
	game.update(ram)

	for i in range(13):
		if game.ship_types[i] == 0:
			# This ship slot not in use.
			continue
		if game.ship_types[i] & 0x80:
			# Planet - not a wireframe, needs special handling.
			continue
		state = game.ship_states[i]
		print "Ship ", i
		print "Position:", state.pos
		print "Rotation:"
		print state.rot
		print "State:", str.join(" ", ["%02X" % b for b in state.rest])
		ship = game.ship_data[game.ship_types[i] - 1]
		if not transforms[i]:
			transforms[i] = vtkTransform()
			transforms[i].PostMultiply()
			filters[i] = vtkTransformPolyDataFilter()
			filters[i].SetInputData(ship_model(ship))
			filters[i].SetTransform(transforms[i])
			mapper = vtkPolyDataMapper()
			mapper.SetInputConnection(filters[i].GetOutputPort())
			actor = vtkActor()
			actor.SetMapper(mapper)
			renderer.AddActor(actor)
		matrix = np.empty((4,4))
		matrix[0:3,0:3] = (state.rot[[2,1,0]] * np.array([-1, 1, 1])).T
		matrix[0:3,3] = state.pos * np.array([-1, 1, 1])
		matrix[3,0:3] = 0
		matrix[3,3] = 1
		transforms[i].SetMatrix(matrix.reshape(16) / 200.0)
		filters[i].Update()
	window.Render()
