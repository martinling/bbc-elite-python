from structures import *
from server import *
import numpy as np
import pylase as ol
import networkx
import sys

ol.init()

game = Game()

server = Server()

def dedupe(a):
	return np.concatenate([a[0],a[1:,1]])

def in_view(pos):
	ndim = pos.ndim
	if ndim == 1:
		pos = np.array([pos])
	result = (pos[:,2] < 0) & np.all(np.abs(pos[:,0:2]) < -pos[:,2:3], axis=1)
	if ndim == 1:
		result = result[0]
	return result

client = server.accept()

while True:

	# Update game state
	ram = client.update()
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

	# Draw lasers
	if game.laser_firing:
		ol.line((-0.5, -1),(0, 0), ol.C_WHITE)
		ol.line((-0.6, -1),(0, 0), ol.C_WHITE)
		ol.line(( 0.5, -1),(0, 0), ol.C_WHITE)
		ol.line(( 0.6, -1),(0, 0), ol.C_WHITE)

	ol.perspective(50, 1, 1, 100)

	# Draw dust
	for position in game.dust_positions:
		velocity = [0, -game.pitch_rate, game.speed]
		ol.begin(ol.LINESTRIP)
		ol.vertex3(position, ol.C_WHITE)
		ol.vertex3(position - velocity, ol.C_WHITE)
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

		if not in_view(state.pos):
			continue

		position = state.pos
		rotation = state.rot
		normals = ship.face_normals
		centers = ship.face_centers
		vertices = ship.vertices

		rotated_normals = np.dot(rotation, normals.T).T
		rotated_centers = np.dot(rotation, normals.T).T + position
		rotated_vertices = np.dot(rotation, vertices.T).T + position
		visible_vertices = np.nonzero(in_view(rotated_vertices))[0]

		dot_product = np.sum(rotated_normals * rotated_centers, axis=1)
		visible_faces = np.nonzero(dot_product < 0)[0]

		first_end_visible = np.any(ship.edges[:,0:1] == visible_vertices, axis=1)
		other_end_visible = np.any(ship.edges[:,1:2] == visible_vertices, axis=1)

		both_ends_visible = first_end_visible & other_end_visible

		first_side_visible = np.any(ship.edge_faces[:,0:1] == visible_faces, axis=1)
		other_side_visible = np.any(ship.edge_faces[:,1:2] == visible_faces, axis=1)

		one_side_visible = first_side_visible | other_side_visible

		edge_visible = both_ends_visible & one_side_visible

		visible_edges = np.nonzero(edge_visible)[0]

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
