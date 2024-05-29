from structures import *
from source import *
import numpy as np
import sys

game = Game()
source = Source()

while True:
	# Read RAM from emulator
	ram = source.update_blocking()

	# Update game state
	game.update(ram)

	for slot in range(13):
		if game.ship_types[slot] != 0:
			state = game.ship_states[slot]
			print()
			print("Ship ", slot, "type", game.ship_types[slot])
			print("Position:", state.pos)
			print("Rotation:")
			print(state.rot)
			print("Speed", state.speed, "Accel", state.accel, "Roll", state.roll, "Pitch", state.pitch)
			print("Energy", state.energy, "Attack", hex(state.attack), "Behaviour", hex(state.behaviour), "Visiblity", hex(state.visibility))
