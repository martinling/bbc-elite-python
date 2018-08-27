import numpy as np
from vtk import *
from structures import *
from rendering import *
import sys

game = Game()

ram = np.fromfile("ram.dat", dtype=np.uint8)

game.update(ram)

for ship in game.ship_data:
	if not ship:
		continue
	print "Vertices:", ship.num_vertices
	print "Edges:", ship.num_edges
	print "Faces:", ship.num_faces
	mapper = vtkPolyDataMapper()
	mapper.SetInputData(ship_model(ship))
	actor = vtkActor()
	prop = actor.GetProperty()
	prop.SetAmbient(0.1)
	prop.SetDiffuse(0.25)
	actor.SetMapper(mapper)
	renderer = vtkRenderer()
	renderer.AddActor(actor)
	window = vtkRenderWindow()
	window.AddRenderer(renderer)
	interactor = vtkRenderWindowInteractor()
	interactor.SetRenderWindow(window)
	interactor.Start()
