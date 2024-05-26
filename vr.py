import numpy as np
from vtk import *
from structures import *
from rendering import *
from source import *

source = Source()
game = Game()
ram = source.update_blocking()
game.update(ram)

renderer = vtkOpenVRRenderer()
renderWindow = vtkOpenVRRenderWindow()
renderWindow.Initialize()

renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtkOpenVRRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

instances = [ShipInstance(i) for i in range(13)]
for instance in instances:
    renderer.AddActor(instance.actor)
renderer.SetBackground(0.0, 0.0, 0.0)

renderWindow.Render()
renderWindowInteractor.Initialize()

while True:
    renderWindowInteractor.DoOneEvent(renderWindow, renderer)

    if (ram := source.update_nonblocking()) is not None:
        game.update(ram)
        for instance in instances:
            if game.ship_types[instance.slot] != 0:
                state = game.ship_states[instance.slot]
            instance.update(game)
