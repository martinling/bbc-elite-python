import numpy as np
from scipy.spatial.transform import Rotation as R
from vtk import *
from structures import *
from rendering import *

game = Game()

ram = np.fromfile("ram.dat", dtype=np.uint8)

game.update(ram)

ship = game.ship_data[10]
print("Vertices:", ship.num_vertices)
print("Edges:", ship.num_edges)
print("Faces:", ship.num_faces)

matrix = np.array([
    [ 0,   0,   1,   0],
    [ 0,   1,   0,   0],
    [-1,   0,   0,-150],
    [ 0,   0,   0,   1]], dtype=float)

transform = vtkTransform()
transform.PostMultiply()
transform.SetMatrix(matrix.reshape(16))

filter = vtkTransformPolyDataFilter()
filter.SetTransform(transform)
filter.SetInputData(ship_model(ship))
filter.Update()
        
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(filter.GetOutputPort())

actor = vtkActor()
actor.SetMapper(mapper)

prop = actor.GetProperty()
prop.SetColor(0.4,0.4,0.4)
prop.SetEdgeColor(1,1,1)
prop.SetLineWidth(10)

renderer = vtkOpenVRRenderer()
renderWindow = vtkOpenVRRenderWindow()
renderWindow.Initialize()

renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtkOpenVRRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

renderer.AddActor(actor)
renderer.SetBackground(0.0, 0.0, 0.0)

renderWindow.Render()
renderWindowInteractor.Initialize()

while True:
    renderWindowInteractor.DoOneEvent(renderWindow, renderer)
    old = R.from_matrix(matrix[0:3,0:3])
    local_delta = 0.005 * np.array([0,-1,2])
    global_delta = old.apply(local_delta, inverse=True)
    new = old * R.from_rotvec(global_delta)
    matrix[0:3,0:3] = new.as_matrix()
    transform.SetMatrix(matrix.reshape(16))
    filter.Update()
