

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

# Not sure if this is how these work yet. 
LINE_COLORS = [(90, 90, 90), (140, 140, 140)]

class MapGeometry:

    def __init__(self, moon = False):

        self.moon = moon

        # Set the colors, as well as memory and render orders based on the map being rendered
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
        self.terrain_tris = {}
        self.line_data = [[], [], [], [], [], [], [], [], [], []]

        # Load in some default values

        for key in self.memory_order:
            self.terrain_vertices[key] = []
            self.terrain_tris[key] = []
    
    @staticmethod
    def from_file(path_to_bin_file: str, moon = False):

        '''
        Create a MapGeometry object from a specified bin file
        '''

        # Parse the file contents, and save them into a newly created MapGeometry object

        if not os.path.exists(path_to_bin_file):
            raise FileNotFoundError('Bin file not found! Check the path specified.')

        # Create empty map object
        map_geo = MapGeometry(moon = moon)

        # Open, and read the binary file
        with open(path_to_bin_file, 'rb') as file_obj:
            binary_data = file_obj.read()

        total_bytes = len(binary_data)

        # Read the 11 mesh chunks in.
        all_mesh_data, mesh_chunks_size = read_n_using_func(binary_data, 0, 11, read_single_mesh_chunk)

        # Loop over all the new mesh data, and add it into the map geo object
        for key, (coordinates, tris) in zip(map_geo.memory_order, all_mesh_data):

            map_geo.terrain_vertices[key] = coordinates
            map_geo.terrain_tris[key] = tris

        # Read the 10 quad chunks in.
        all_line_data, lines_chunk_size = read_n_using_func(binary_data, mesh_chunks_size, 10, read_line_quads)

        # Save the quad data into the map geo object
        map_geo.line_data = all_line_data

        # There are sometimes 4 extra 0x00 bytes after this, but I cannot find anything which suggests their meaning. 
        # I want to detect that stuff here, in case I stumble upon a file which uses them. 

        if total_bytes - lines_chunk_size - mesh_chunks_size > 0 and binary_data[lines_chunk_size + mesh_chunks_size:] != b'\x00\x00\x00\x00':
            print(f'({total_bytes - lines_chunk_size - mesh_chunks_size}) Extra nonzero bytes detected! {binary_data[lines_chunk_size + mesh_chunks_size:]}')
        
        return map_geo

    def render_to_image(self, size: int):

        '''
        Render the MapGeometry object to a PIL image. 
        Use the size field to indicate the size of the resulting image. 
        '''

        # Create a canvas with some attached helper functions that make this code way cleaner
        tc = TileCanvas(size, self.base_color)

        # Loop over all the geometry layers, in the order they should be rendered
        for layer_key in self.render_order:

            # Determine the color of this layer
            color = self.layer_colors[layer_key]

            # Loop over each triangle in the mesh
            for triangle in self.terrain_tris[layer_key]:

                # Lookup the 2d coordinates of the triangle in the terrain vertices table
                lookup_coords = [self.terrain_vertices[layer_key][index] for index in triangle]

                # Draw the triangle with the specified color
                tc.triangle(lookup_coords, color)

        alternate = False # Using this to alternate solid and dashed lines (no idea if this is how they actually render them.)

        # Loop over each line group
        for segments in self.line_data:

            # Loop over every quad in the line group
            for quad in segments:

                # Covert the quad element into a line
                quad_line = line_from_quad(quad)

                # Draw the resulting line
                tc.draw_line(*quad_line, color = LINE_COLORS[alternate], dashed = alternate)
            
            alternate = not alternate # Flip alternate between each layer
        
        return tc.tile_img
    
    def clear_all_lines(self):

        '''
        Clear all the lines in the map geometry object
        '''

        self.line_data = [[], [], [], [], [], [], [], [], [], []]
    
    def clear_geometry(self, layer: str):

        '''
        Clear the geometry of a given layer, i.e.:

        map.clear_geometry('Snow') 

        Clears all the snow off that map tile
        '''

        self.terrain_vertices[layer] = []
        self.terrain_tris[layer] = []
    
    def clear_all_geometry(self):

        '''
        Clear all geometry layers from the tile
        '''

        for layer in self.memory_order:
            self.clear_geometry(layer)

    def save_as(self, filepath: str):
        
        '''
        Save the current version of the MapGeometry back to a .bin file
        '''

        if not filepath.endswith('.bin'):
            raise ValueError('Please specify a filepath that ends in .bin')
        
        output_bytes = b''

        # Pack all the mesh data
        for key in self.memory_order:

            output_bytes += pack_single_mesh(self.terrain_vertices[key], self.terrain_tris[key])

        # Pack all the quad data        
        for line_quads in self.line_data:

            output_bytes += pack_quads(line_quads)
        
        # Save into file
        with open(filepath, 'wb') as output_file:
            output_file.write(output_bytes)
    
    def add_line(self, layer_index: int, from_coord: Tuple[float, float], to_coord: Tuple[float, float], thickness: float = 4):
        
        '''
        Add a line in the line layer specified, between two desired coordinates
        '''

        # Convert to a quad, and add to the desired layer

        # Determine angles 90 degrees off the line bearing
        dy = to_coord[1] - from_coord[1]
        dx = to_coord[0] - from_coord[0]
        angle = math.atan2(dy, dx)
        a1 = angle + math.pi / 2
        a2 = angle - math.pi / 2

        def offset_with_angle(x, y, angle):
            # Thickness probably does nothing here, but maybe it does?
            return (x + thickness * math.cos(angle), y + thickness * math.sin(angle))

        # Use the offset angles to determine a quad which preserves the CCW rotation
        c1 = offset_with_angle(*from_coord, a2)
        c2 = offset_with_angle(*from_coord, a1)
        c3 = offset_with_angle(*to_coord, a1)
        c4 = offset_with_angle(*to_coord, a2)

        # Add the new quad to the desired layer
        self.line_data[layer_index].append((c1, c2, c3, c4))
    
    def add_path(self, layer_index: int, path: List[Tuple[Tuple[float, float]]]):

        '''
        Given a list of 2 coordinate pairs, like: 
    
            [((.1,0),(.5,1)),((.5,1),(.9,0)),((.3,.5),(.7,.5))]

        Add the sequence of lines onto the tile
        '''

        for from_coord, to_coord in path:

            self.add_line(layer_index, from_coord, to_coord)
    
    def add_text(self, layer: int, text: str, location_x: float, location_y: float, size: float):

        '''
        Add some text to a certain line layer in the tile, at a certain location with a certain height.

        Some special characters are allowed, like spaces and '\n' but other than that, stuck to regular
        letters, or add the character you want to letter_data.py
        '''

        text = text.upper() # Covert to uppercase, for simplicity

        start_x = location_x # Keep a reference to where the text should start, for new lines

        # Loop over each character individually
        for character in text:

            # If space, just advance location, and continue
            if character == ' ':
                location_x += size
                continue
            
            # If newline, return x to original position, advance y position, and continue
            if character == '\n':
                location_x = start_x
                location_y -= size * 1.3
                continue
            
            if character not in LETTERS:
                raise ValueError(f'Non-letter character specified: {character}')

            # Lookup letter path in table            
            letter_path = LETTERS[character].copy()

            # Scale letter to desired size, and move it to the correct position
            letter_path = offset_path(scale_path(letter_path, size), location_x, location_y)

            # Add the letter path to the tile
            self.add_path(layer, letter_path)

            # Advance X position for next character
            location_x += size
    
    def add_bolded_text(self, layer, text, location_x, location_y, size, thickness = 5):

        '''
        Add some thicker text to the tile.
        '''

        # Lazy way to make bolded text, but surprisingly effective!

        for i in range(thickness):

            self.add_text(layer, text, location_x + i, location_y + i, size)
    
    def add_geometry(self, layer: str, verts: List[Tuple[float, float]], tris: List[Tuple[int, int, int]]):
        '''
        Adds some geometry to a layer, specifying the verts, and tris. 
        Ducky will automatically adjust triangles indices to add to existing geometry
        '''

        # Determine where there are free indices that we can add our indices to
        current_geometry_max_index = len(self.terrain_vertices[layer])

        # Add the terrain vertices        
        self.terrain_vertices[layer] += verts

        # Loop over all given triangles
        for tri in tris:

            # offset the triangle to align with the new positions of the vertices in the current mesh

            self.terrain_tris[layer].append((
                tri[0] + current_geometry_max_index, 
                tri[1] + current_geometry_max_index, 
                tri[2] + current_geometry_max_index
            ))