import sys
import numpy as np
from structures import *
import pylase as ol

ol.init()

game = Game()

while True:
	# Read RAM from emulator
	ram = np.frombuffer(sys.stdin.buffer.read(0x10000), dtype=np.uint8)

	# Update game state
	game.update(ram)

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
