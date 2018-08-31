import sys
import numpy as np
from structures import *
import pylase as ol
import networkx

ol.init()

game = Game()

def dedupe(a):
	return np.concatenate([a[0],a[1:,1]])

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.buffer.read(0x10000), dtype=np.uint8)

	# Update game state
	game.update(ram)

	ol.loadIdentity3()
	ol.loadIdentity()

	ol.rect((-0.95, -0.95), (0.95, 0.95), ol.C_WHITE)

	font = ol.getDefaultFont()
	s = "Front View"
	w = ol.getStringWidth(font, 0.1, s)
	ol.drawString(font, (-w/2,0.85), 0.1, ol.C_WHITE, s)

	ol.perspective(50, 1, 1, 100)

	for ship_type, state in zip(game.ship_types, game.ship_states):

		if ship_type == 0 or ship_type & 0x80:
			continue

		print("Type:", ship_type)
		print("Position:", state.pos)
		print("Rotation:")
		print(state.rot)

		ship = game.ship_data[ship_type - 1]

		if not ship:
			continue

		position = state.pos * [1, 1, -1]
		rotation = state.rot[[2,1,0]] * [1, 1, -1]
		normals = ship.face_normals * [1, 1, -1]

		rotated_normals = np.dot(rotation, normals.T).T
		visible_faces = np.nonzero(rotated_normals[:,2] < 0)[0]

		first_end_visible = np.any(ship.edge_faces[:,0:1] == visible_faces, axis=1)
		other_end_visible = np.any(ship.edge_faces[:,1:2] == visible_faces, axis=1)

		visible_edges = np.nonzero(first_end_visible | other_end_visible)[0]

		graph = networkx.Graph()
		graph.add_nodes_from(range(ship.num_vertices))
		graph.add_edges_from(ship.edges[visible_edges])

		ol.pushMatrix3()

		ol.translate3(tuple(position))

		matrix = np.zeros((4,4))
		matrix[0:3,0:3] = rotation
		matrix[3,3] = 1

		ol.multMatrix3(matrix.reshape(16))

		chains = networkx.algorithms.chain_decomposition(graph)

		for chain in chains:
			vertices = dedupe(np.array(chain))
			ol.begin(ol.LINESTRIP)
			for vertex in vertices:
				ol.vertex3(ship.vertices[vertex], ol.C_WHITE)
			ol.end()

		ol.popMatrix3()

	ol.renderFrame(60)
