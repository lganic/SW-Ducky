# Render the main island, using ducky image generation

from sw_ducky import MapGeometry
from PIL import Image
import os

from stormworks_path import STORMWORKS_PATH

SIZE = 60
WIDTH = 31
HEIGHT = 16

def request_image(x, y):

    # Find the bin file

    filename = f'arid_island_{x}_{y}_map_geometry.bin'

    print(f'Loading: {filename}', end = ' ')

    full_path = os.path.join(STORMWORKS_PATH, 'rom', 'data', 'tiles', filename)

    try:
        geo = MapGeometry.from_file(full_path)
        print('Success')
    except FileNotFoundError:
        geo = MapGeometry() # File not found. Assume empty
        print('Fail!')

    image = geo.render_to_image(SIZE)

    return image

offset_y = 3 # because of course the corner isn't at 0,0 for this island. 
offset_x = 2

grid_width = (WIDTH-offset_x) * SIZE
grid_height = (HEIGHT - offset_y) * SIZE

map_img = Image.new('RGB', (grid_width, grid_height))

for y in range(offset_y, HEIGHT):
    for x in range(offset_x, WIDTH):

        tile_image = request_image(x, y)

        y_location = SIZE * ((HEIGHT - 1) - y)

        map_img.paste(tile_image, ((x - offset_x) * SIZE, y_location))


# map_img = map_img.resize((WIDTH * 100, HEIGHT * 100))

map_img.show()