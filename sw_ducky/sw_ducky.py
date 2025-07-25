

import math
import os
from typing import List, Tuple

from .utilitity import line_from_quad
from .parsing import read_n_using_func, read_line_quads, read_single_mesh_chunk, pack_single_mesh, pack_quads
from .path_utils import scale_path, offset_path
from .letter_data import LETTERS
from .tile_drawing import TileCanvas

EARTH_LAYER_MEM_ORDER = ['Road', 'Grass', 'Sand', 'Pond', 'Snow', 'Rock', 'HardRock', 'Sea-3', 'Sea-2', 'Sea-1','Sea-0']
EARTH_LAYER_RENDER_ORDER = ['Sea-0', 'Sea-1', 'Sea-2','Sea-3', 'Road', 'Grass', 'Sand', 'Pond', 'Snow', 'Rock', 'HardRock']

MOON_LAYER_MEM_ORDER = ['Blank-1', 'Blank-2', 'Blank-3', 'Blank-4', 'Blank-5', 'Blank-6', 'Blank-7', 'Moon-3', 'Moon-2', 'Moon-1', 'Moon-0']
MOON_LAYER_RENDER_ORDER = ['Moon-0', 'Moon-1', 'Moon-2', 'Moon-3', 'Blank-1', 'Blank-2', 'Blank-3', 'Blank-4', 'Blank-5', 'Blank-6', 'Blank-7']

EARTH_COLORS = {
    'Sea-0': (50, 121, 134),
    'Sea-1': (61, 142, 159),
    'Sea-2': (72, 163, 184),
    'Sea-3': (83, 185, 209),
    'Road': (208, 208, 198),
    'Grass': (164, 184, 117),
    'Sand': (227, 208, 141),
    'Pond': (83, 185, 209),
    'Snow': (255, 255, 255),
    'Rock': (139, 110, 92),
    'HardRock': (88, 62, 45)
}

MOON_COLORS = {
    'Moon-0': (134, 137, 151),
    'Moon-1': (109, 112, 126),
    'Moon-2': (84, 87, 101),
    'Moon-3': (59, 62, 76),
    'Blank-1': (255, 1, 255),
    'Blank-2': (255, 2, 255),
    'Blank-3': (255, 3, 255),
    'Blank-4': (255, 4, 255),
    'Blank-5': (255, 5, 255),
    'Blank-6': (255, 6, 255),
    'Blank-7': (255, 7, 255)
}

BASE_COLORS = {
    'Earth': (40, 100, 110),
    'Moon': (159, 162, 176)
}

LINE_COLORS = [(90, 90, 90), (140, 140, 140)]

class MapGeometry:

    def __init__(self, moon = False):

        self.moon = moon

        if self.moon:
            self.memory_order = MOON_LAYER_MEM_ORDER
            self.render_order = MOON_LAYER_RENDER_ORDER
            self.layer_colors = MOON_COLORS
            self.base_color = BASE_COLORS['Moon']
        else:
            self.memory_order = EARTH_LAYER_MEM_ORDER
            self.render_order = EARTH_LAYER_RENDER_ORDER
            self.layer_colors = EARTH_COLORS
            self.base_color = BASE_COLORS['Earth']

        self.terrain_vertices = {}
        self.terrain_edges = {}
        self.line_data = [[], [], [], [], [], [], [], [], [], []]

        # Load in some default values

        for key in self.memory_order:
            self.terrain_vertices[key] = []
            self.terrain_edges[key] = []
    
    @staticmethod
    def from_file(path_to_bin_file: str, moon = False):

        # Parse the file contents, and save them into a newly created MapGeometry object

        if not os.path.exists(path_to_bin_file):
            raise FileNotFoundError('Bin file not found! Check the path specified.')

        map_geo = MapGeometry(moon = moon)

        with open(path_to_bin_file, 'rb') as file_obj:

            binary_data = file_obj.read()

            total_bytes = len(binary_data)

            all_mesh_data, mesh_chunks_size = read_n_using_func(binary_data, 0, 11, read_single_mesh_chunk)

            for key, (coordinates, tris) in zip(map_geo.memory_order, all_mesh_data):

                map_geo.terrain_vertices[key] = coordinates
                map_geo.terrain_edges[key] = tris
            
            all_line_data, lines_chunk_size = read_n_using_func(binary_data, mesh_chunks_size, 10, read_line_quads)

            map_geo.line_data = all_line_data

            # There are sometimes 4 extra 0x00 bytes after this, but I cannot find anything which suggests their meaning. 
            # I want to detect that stuff here, in case I stumble upon a file which uses them. 

            if total_bytes - lines_chunk_size - mesh_chunks_size > 0 and binary_data[lines_chunk_size + mesh_chunks_size:] != b'\x00\x00\x00\x00':
                print(f'({total_bytes - lines_chunk_size - mesh_chunks_size}) Extra nonzero bytes detected! {binary_data[lines_chunk_size + mesh_chunks_size:]}')
        
        return map_geo

    def render_to_image(self, size):

        tc = TileCanvas(size, self.base_color)

        for layer_key in self.render_order:

            color = self.layer_colors[layer_key]

            for edges in self.terrain_edges[layer_key]:

                lookup_coords = [self.terrain_vertices[layer_key][index] for index in edges]

                tc.triangle(lookup_coords, color)

        alternate = False

        for segments in self.line_data:

            for quad in segments:

                quad_line = line_from_quad(quad)

                tc.draw_line(*quad_line, color = LINE_COLORS[alternate], dashed = alternate)
            
            alternate = not alternate
        
        return tc.tile_img
    
    def clear_all_lines(self):

        self.line_data = [[], [], [], [], [], [], [], [], [], []]
    
    def clear_geometry(self, layer):

        self.terrain_vertices[layer] = []
        self.terrain_edges[layer] = []

    def save_as(self, filepath):
        '''Save the current version of the MapGeometry back to a .bin file'''

        if not filepath.endswith('.bin'):
            raise ValueError('Please specify a filepath that ends in .bin')
        
        output_bytes = b''

        for key in self.memory_order:

            output_bytes += pack_single_mesh(self.terrain_vertices[key], self.terrain_edges[key])
        
        for line_quads in self.line_data:

            output_bytes += pack_quads(line_quads)
        
        with open(filepath, 'wb') as output_file:
            output_file.write(output_bytes)
    
    def add_line(self, layer_index, from_coord, to_coord, thickness = 4):
        
        # Convert to a quad, and add to the desired layer

        def offset_with_angle(x, y, angle):

            return (x + thickness * math.cos(angle), y + thickness * math.sin(angle))

        dy = to_coord[1] - from_coord[1]
        dx = to_coord[0] - from_coord[0]

        angle = math.atan2(dy, dx)

        a1 = angle + math.pi / 2
        a2 = angle - math.pi / 2

        c1 = offset_with_angle(*from_coord, a2)
        c2 = offset_with_angle(*from_coord, a1)
        c3 = offset_with_angle(*to_coord, a1)
        c4 = offset_with_angle(*to_coord, a2)

        self.line_data[layer_index].append((c1, c2, c3, c4))
    
    def add_path(self, layer_index, path):

        for from_coord, to_coord in path:

            self.add_line(layer_index, from_coord, to_coord)
    
    def add_text(self, layer, text, location_x, location_y, size):

        text = text.upper()

        start_x = location_x

        location_x -= size # Makes code easier, due to the use of space guard clause

        for character in text:

            location_x += size

            if character == ' ':
                continue

            if character == '\n':
                location_x = start_x - size
                location_y -= size * 1.3
                continue
            
            if character not in LETTERS:
                raise ValueError(f'Non-letter character specified: {character}')
            
            letter_path = LETTERS[character].copy()

            letter_path = offset_path(scale_path(letter_path, size), location_x, location_y)

            self.add_path(layer, letter_path)
    
    def add_bolded_text(self, layer, text, location_x, location_y, size, thickness = 5):

        # Lazy way to make bolded text, but surprisingly effective!

        for i in range(thickness):

            self.add_text(layer, text, location_x + i, location_y + i, size)
    
    def add_geometry(self, layer: str, verts: List[Tuple[float, float]], tris: List[Tuple[int, int, int]]):

        # Adds some geometry to a layer, specifying the verts, and tris. 
        # Ducky will automatically adjust triangles indices to add to existing geometry

        current_geometry_max_index = -1

        for tri in self.terrain_edges[layer]:

            current_geometry_max_index = max(current_geometry_max_index, tri[0], tri[1], tri[2])
        
        self.terrain_vertices[layer] += verts

        current_geometry_max_index += 1

        for tri in tris:

            self.terrain_edges[layer].append((tri[0] + current_geometry_max_index, tri[1] + current_geometry_max_index, tri[2] + current_geometry_max_index))

        print(self.terrain_edges[layer])



if __name__ == '__main__':
    from stormworks_path import STORMWORKS_PATH
    full_path = os.path.join(STORMWORKS_PATH, 'rom', 'data', 'tiles', 'arid_island_21_13_map_geometry - Copy.bin')

    geo = MapGeometry.from_file(full_path)
    geo.add_bolded_text(1,'lganic\nwas\nhere', -400, 300, 75, thickness=10)

    geo.add_geometry('HardRock',
                     [
                       (0, -300),
                       (-100, -100),
                       (-50, -50),
                       (0, -100),
                       (50, -50),
                       (100, -100),
                     ],[
                        (3, 1, 0),
                        (3, 2, 1),
                        (5, 4, 3),
                        (5, 3, 0),
                     ]
                     )

    geo.add_geometry('Snow',
                     [
                       (-300, -300),
                       (-400, -100),
                       (-350, -50),
                       (-300, -100),
                       (-250, -50),
                       (-200, -100),
                     ],[
                        (3, 1, 0),
                        (3, 2, 1),
                        (5, 4, 3),
                        (5, 3, 0),
                     ]
                     )
    
    geo.add_geometry('Pond',
                     [
                       (300, -300),
                       (200, -100),
                       (250, -50),
                       (300, -100),
                       (350, -50),
                       (400, -100),
                     ],[
                        (3, 1, 0),
                        (3, 2, 1),
                        (5, 4, 3),
                        (5, 3, 0),
                     ]
                     )

    img = geo.render_to_image(1000)
    img.show()

    full_path = os.path.join(STORMWORKS_PATH, 'rom', 'data', 'tiles', 'arid_island_21_13_map_geometry.bin')

    geo.save_as(full_path)
