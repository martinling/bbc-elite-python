import sys
import numpy as np
from structures import *
import pylase as ol
import networkx

ol.init()

game = Game()

ol.perspective(50, 1, 1, 100)

def dedupe(a):
	return np.concatenate([a[0],a[1:,1]])

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.buffer.read(0x10000), dtype=np.uint8)

	# Update game state
	game.update(ram)

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

		ol.pushMatrix3()

		ol.translate3(tuple(state.pos * [1, 1, -1]))

		matrix = np.zeros((4,4))
		matrix[0:3,0:3] = state.rot[[2,1,0]] * [1, 1, -1]
		matrix[3,3] = 1

		ol.multMatrix3(matrix.reshape(16))

		graph = networkx.Graph()
		graph.add_nodes_from(range(ship.num_vertices))
		graph.add_edges_from(ship.edges)

		chains = networkx.algorithms.chain_decomposition(graph)

		for chain in chains:
			vertices = dedupe(np.array(chain))
			ol.begin(ol.LINESTRIP)
			for vertex in vertices:
				ol.vertex3(ship.vertices[vertex], ol.C_WHITE)
			ol.end()

		ol.popMatrix3()

	ol.renderFrame(60)
