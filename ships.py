import numpy as np
from vtk import *
from structures import *
import sys

ram = np.frombuffer(sys.stdin.read(0x10000), dtype=np.uint8)
offsets = ram[0x5600:0x5600+64].view(np.uint16)
for offset in offsets:
	if offset == 0:
		continue
	try:
		ship = ShipData(ram, offset)
	except ValueError:
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
