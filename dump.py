from source import *
import sys

source = Source()

ram = source.update_blocking()
open('ram.dat', 'wb').write(ram)
