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

	# Draw crosshair
	ol.line((0,  0.1),(0,  0.2), ol.C_WHITE)
	ol.line((0, -0.1),(0, -0.2), ol.C_WHITE)
	ol.line(( 0.1, 0),( 0.2, 0), ol.C_WHITE)
	ol.line((-0.1, 0),(-0.2, 0), ol.C_WHITE)

	ol.perspective(50, 1, 1, 100)

	# Draw dust
	for position in game.dust_positions:
		position = position * [1, 1, -1]
		ol.begin(ol.LINESTRIP)
		ol.vertex3(position, ol.C_WHITE)
		ol.vertex3(position - [0, 0, game.speed], ol.C_WHITE)
		ol.end()

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

		if state.pos[2] < 0:
			continue

		if np.any(np.abs(state.pos[0:2]) > state.pos[2]):
			continue

		position = state.pos * [1, 1, -1]
		rotation = (state.rot * [1, 1, -1]).T
		normals = ship.face_normals[:,[2,1,0]] * [1, 1, -1]
		centers = ship.face_centers[:,[2,1,0]] * [1, 1, -1]
		vertices = ship.vertices[:,[2,1,0]] * [1, 1, -1]

		rotated_normals = np.dot(rotation, normals.T).T
		rotated_centers = np.dot(rotation, normals.T).T + position
		rotated_vertices = np.dot(rotation, vertices.T).T + position

		dot_product = np.sum(rotated_normals * rotated_centers, axis=1)
		visible_faces = np.nonzero(dot_product < 0)[0]

		first_side_visible = np.any(ship.edge_faces[:,0:1] == visible_faces, axis=1)
		other_side_visible = np.any(ship.edge_faces[:,1:2] == visible_faces, axis=1)

		visible_edges = np.nonzero(first_side_visible | other_side_visible)[0]

		graph = networkx.Graph()
		graph.add_nodes_from(range(ship.num_vertices))
		graph.add_edges_from(ship.edges[visible_edges])

		chains = networkx.algorithms.chain_decomposition(graph)

		for chain in chains:
			chain_vertices = dedupe(np.array(chain))
			ol.begin(ol.LINESTRIP)
			for vertex in chain_vertices:
				ol.vertex3(rotated_vertices[vertex], ol.C_WHITE)
			ol.end()

	ol.renderFrame(60)
