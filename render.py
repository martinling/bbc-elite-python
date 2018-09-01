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

renderer.AddActor(lines_2d(crosshair_points, crosshair_lines))
renderer.AddActor(lines_2d(border_points, border_lines))

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
			print "Speed", state.speed, "Accel", state.accel, "Roll", state.roll, "Pitch", state.pitch
			print "Energy", state.energy, "Attack", hex(state.attack), "Behaviour", hex(state.behaviour), "Visiblity", hex(state.visibility)
		instance.update(game)

	window.Render()
