from structures import *
from rendering import *
from source import *
from vtk import *
import numpy as np
import sys

camera = vtkCamera()
camera.SetPosition(0, 0, 0)
camera.SetFocalPoint(0, 0, -100)
renderer = vtkRenderer()
renderer.SetActiveCamera(camera)
window = vtkRenderWindow()
window.AddRenderer(renderer)

renderer.AddActor(lines_2d(crosshair_points, crosshair_lines))
renderer.AddActor(lines_2d(border_points, border_lines))

instances = [ShipInstance(i) for i in range(13)]
for instance in instances:
	renderer.AddActor(instance.actor)
	renderer.AddActor(instance.laser_actor)

dust_mapper = vtkPolyDataMapper()
dust_actor = vtkActor()
dust_actor.SetMapper(dust_mapper)
renderer.AddActor(dust_actor)

laser_actor = lines_2d(laser_points, laser_lines)
renderer.AddActor(laser_actor)

game = Game()
source = Source()

while True:
	# Read RAM from emulator
	ram = source.update_blocking()

	# Update game state
	game.update(ram)

	for instance in instances:
		instance.update(game)

	dust_mapper.SetInputData(make_dust(game))

	laser_actor.SetVisibility(game.laser_firing)

	renderer.ResetCameraClippingRange()

	window.Render()
