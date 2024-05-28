import numpy as np

def screen_image(ram):
	# Read the video RAM as 31 rows of 32 characters of 8x8 pixels each.
	chars = np.unpackbits(ram[0x6000:0x7f00]).reshape(31,32,8,8)

	# Take the view pixels and reorder into a 256 x 192 pixel, 1-bit image.
	view_1bpp = chars[:24].swapaxes(1,2).reshape(192,256)

	# Convert view to an 256 x 192 pixel, 8-bit RGB image.
	view_rgb = np.repeat(view_1bpp * 0xFF, 3, 1).reshape(192,256,3)

	# Take the panel rows and reorder into a 128x56 pixel, 2-component image.
	panel_2bpp = chars[24:] \
		.reshape(7,32,8,2,4) \
		.swapaxes(1,2) \
		.swapaxes(3,4) \
		.reshape(56,128,2)

	# Combine the 2 components to get 2-bit colour indexes.
	panel_indexed = panel_2bpp[:,:,1] << 1 | panel_2bpp[:,:,0]

	# Define the panel's colour pallette.
	panel_colors = np.array([
		[0x00, 0x00, 0x00],
		[0xFF, 0xFF, 0x00],
		[0xFF, 0x00, 0x00],
		[0x00, 0xFF, 0x00],
	])

	# Convert panel to RGB by indexing into palette.
	panel_rgb = panel_colors[panel_indexed]

	# Double the panel pixels horizontally, to match the view width.
	panel_scaled_rgb = np.repeat(panel_rgb, 2, 1)

	# Stack the two parts of the screen into a single 256x248 image.
	combined_rgb = np.concatenate([view_rgb, panel_scaled_rgb])

	return combined_rgb
