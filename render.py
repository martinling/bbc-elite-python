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

instances = [ShipInstance(i) for i in range(13)]
for instance in instances:
	renderer.AddActor(instance.actor)

game = Game()

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.read(0x10000), dtype=np.uint8)

	# Update game state
	game.update(ram)

	for instance in instances:
		if game.ship_types[instance.slot] != 0:
			state = game.ship_states[instance.slot]
			print "Ship ", instance.slot, "type", game.ship_types[instance.slot]
			print "Position:", state.pos
			print "Rotation:"
			print state.rot
			print "State:", str.join(" ", ["%02X" % b for b in state.rest])
		instance.update(game)

	window.Render()
