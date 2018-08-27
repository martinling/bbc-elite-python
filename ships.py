import numpy as np
from vtk import *
from structures import *
import sys

game = Game()

ram = np.frombuffer(sys.stdin.read(0x10000), dtype=np.uint8)

game.update(ram)

for ship in game.ship_data:
	if not ship:
		continue
	mapper = vtkPolyDataMapper()
	mapper.SetInputData(ship.poly)
	actor = vtkActor()
	actor.SetMapper(mapper)
	renderer = vtkRenderer()
	renderer.AddActor(actor)
	window = vtkRenderWindow()
	window.AddRenderer(renderer)
	interactor = vtkRenderWindowInteractor()
	interactor.SetRenderWindow(window)
	interactor.Start()
