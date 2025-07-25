# Render the main island, using ducky image generation

from sw_ducky import MapGeometry
from PIL import Image
import os

from stormworks_path import STORMWORKS_PATH

SIZE = 1000
WIDTH = 20
HEIGHT = 10

def request_image(x, y):

    # Find the bin file

    filename = f'mega_island_{x}_{y}_map_geometry.bin'

    print(f'Loading: {filename}', end = ' ')

    full_path = os.path.join(STORMWORKS_PATH, filename)

    try:
        geo = MapGeometry.from_file(full_path)
        print('Success')
    except FileNotFoundError:
        geo = MapGeometry() # File not found. Assume empty
        print('Fail!')

    image = geo.render_to_image(SIZE)

    return image


grid_width = WIDTH * SIZE
grid_height = HEIGHT * SIZE

map_img = Image.new('RGB', (grid_width, grid_height))

for y in range(HEIGHT):
    for x in range(WIDTH):

        tile_image = request_image(x, y)

        y_location = SIZE * ((HEIGHT - 1) - y)

        map_img.paste(tile_image, (x * SIZE, y_location))


# map_img = map_img.resize((WIDTH * 100, HEIGHT * 100))

map_img.show()