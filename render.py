import sys
import numpy as np
from vtk import *
from structures import *
from rendering import *

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

game = Game()

def make_dust(game):
	points = vtkPoints()
	points.SetNumberOfPoints(game.num_dust * 2)
	lines = vtkCellArray()
	positions = (game.dust_positions) / 200.0
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

dust_mapper = vtkPolyDataMapper()
dust_actor = vtkActor()
dust_actor.SetMapper(dust_mapper)
renderer.AddActor(dust_actor)

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.buffer.read(0x10000), dtype=np.uint8)

	# Update game state
	game.update(ram)

	for instance in instances:
		if game.ship_types[instance.slot] != 0:
			state = game.ship_states[instance.slot]
			print("Ship ", instance.slot, "type", game.ship_types[instance.slot])
			print("Position:", state.pos)
			print("Rotation:")
			print(state.rot)
			print("Speed", state.speed, "Accel", state.accel, "Roll", state.roll, "Pitch", state.pitch)
			print("Energy", state.energy, "Attack", hex(state.attack), "Behaviour", hex(state.behaviour), "Visiblity", hex(state.visibility))
		instance.update(game)

	dust_mapper.SetInputData(make_dust(game))

	window.Render()
