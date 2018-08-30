import sys
import numpy as np
from structures import *
import pylase as ol

ol.init()

game = Game()

ol.perspective(60, 1, 1, 100)
ol.translate3((0, 0, -100))

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.buffer.read(0x10000), dtype=np.uint8)

	# Update game state
	game.update(ram)

	ol.renderFrame(60)

	for ship_type, state, ship in zip(
			game.ship_types,
			game.ship_states,
			game.ship_data):

		if ship_type == 0:
			continue

		print("Type:", ship_type)
		print("Position:", state.pos)
		print("Rotation:")
		print(state.rot)

		if not ship:
			continue

		for edge in ship.edges[:4]:
			ol.begin(ol.LINESTRIP)
			for vertex in ship.vertices[edge]:
				print(vertex)
				ol.vertex3(vertex, ol.C_WHITE)
			ol.end()
