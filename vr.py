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

crosshair_3d = np.empty((len(crosshair_points), 3))
crosshair_3d[:,0:2] = (crosshair_points - 0.5) * 4.0
crosshair_3d[:,2] = -5

renderer.AddActor(lines_3d(crosshair_3d, crosshair_lines))

laser_3d = np.empty((len(laser_points), 3))
laser_3d[:,0:2] = (laser_points - 0.5) * 4.0
laser_3d[:,2] = [0, 0, 0, 0, -100]

laser_actor = lines_3d(laser_3d, laser_lines)
renderer.AddActor(laser_actor)

instances = [ShipInstance(i) for i in range(13)]
for instance in instances:
    renderer.AddActor(instance.actor)

dust_mapper = vtkPolyDataMapper()
dust_actor = vtkActor()
dust_actor.SetMapper(dust_mapper)
renderer.AddActor(dust_actor)

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
        dust_mapper.SetInputData(make_dust(game))
        laser_actor.SetVisibility(game.laser_firing)
        renderer.ResetCameraClippingRange()
