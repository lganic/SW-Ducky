import struct
from typing import List, Tuple, Any

from .utilitity import is_cord_valid, is_poly_valid

def read_single_mesh_chunk(bin: bytes, index: int) -> Tuple[Tuple[List[Tuple[float, float]], List[Tuple[int, int, int]]], int]:

    '''
    Read a chunk containing mesh data from a byte string, at a given index.
    '''

    # Read the chunk length of the coordinates section. 
    chunk_length = struct.unpack('<H', bin[index: index + 2])[0]

    # Advance the read index by the size of the length header
    read_index = 2 + index

    coordinates = []

    for _ in range(chunk_length):

        # Unpack 3 float coordinate from file
        coordinate = struct.unpack('<fff', bin[read_index: read_index + 12])

        x, _, y = coordinate # Ditch middle coordinate (always zero)

        if not is_cord_valid((x, y)):
            # Coordinate had some invalid entries. 

            raise ValueError(f'An invalid coordinate was read from the file: {(x, y)} at index: {read_index}')

        read_index += 12 # Advance read index to next coordinate

        coordinates.append((x, y)) # Append coordinate to output

    # The read point now lies at the triangle index section.    
    tris_chunk_length = struct.unpack('<H', bin[read_index: read_index + 2])[0]

    tris = []

    # Advance the read index by the size of the length header
    read_index += 2

    for _ in range(tris_chunk_length // 3):

        # Unpack the 3 indices of the triangle
        tri = struct.unpack('<HHH', bin[read_index: read_index + 6])

        # Advance the read index
        read_index += 6

        tris.append(tri)

    # Return the coordinates, and the amount of bytes read.
    return (coordinates, tris), read_index - index

def read_line_quads(bin: bytes, index: int) -> Tuple[List[Tuple[Tuple[float, float]]], int]:

    '''
    Read a chunk containing quad data from a byte string, at a given index.
    '''

    # Read the length of the quads chunk
    chunk_length = struct.unpack('<H', bin[index: index + 2])[0]

    # Advance the read index by the size of the length header
    part_index = 2 + index

    quads = []

    for _ in range(chunk_length // 4):

        # Unpack the x, and y values of each quad corner.
        # The middle value of x and y is guaranteed to be zero. 
        # alt has data in it, but is not used by stormworks, so we can ignore it.
        # One or zero follows a repeating pattern of 1, 0, 0, 1 across each quad, so we ignore it too
        (
            x1, _, y1, _alt, _one_or_zero,
            x2, _, y2, _alt, _one_or_zero,
            x3, _, y3, _alt, _one_or_zero,
            x4, _, y4, _alt, _one_or_zero
        ) = struct.unpack('<' + 'fffIf' * 4, bin[part_index : part_index + 80])

        # Advance the read index by the size of the quad chunk
        part_index += 80

        # Assemble the quad
        quad = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))

        if not is_poly_valid(quad):
            # This happens from time to time, likely due to SW devs shitty dev codebase. We can safely ignore these packets though, because of the way that the later rendering works.
            continue

        quads.append(quad)

    # Return the quads, and the number of bytes read    
    return quads, part_index - index

def read_n_using_func(bin: bytes, index: int, number: int, function) -> Tuple[List[Any], int]:

    '''
    Read multiple repeated segments using the same reader function.
    For instance:

    read_n_using_func(bin_data, 100, 11, read_single_mesh_chunk)

    Will read and return 11 consecutive mesh chunks, starting from index 100 in bin_data
    '''

    part_index = index

    results = []

    for _ in range(number):

        # Run the given function
        result, offset = function(bin, part_index)

        results.append(result)

        # Advance the pointer by the number of bytes read
        part_index += offset
    
    return results, part_index - index

def add_length(byte_string: bytes, value: int) -> bytes:

    '''
    Add a length prefix of a given value to a byte string
    '''

    length_bytes = struct.pack('<H', value)

    return length_bytes + byte_string
    

def pack_single_mesh(verts: List[Tuple[float, float]], tris: List[Tuple[int, int, int]]) -> bytes:

    '''
    Pack a mesh chunk, using vertex and triangle data
    '''

    verts_bytes = b''

    # Pack all the vertices
    for vert in verts:

        verts_bytes += struct.pack('<fff', vert[0], 0, vert[1])

    # Add a length prefix indicating the number of vertices 
    verts_bytes = add_length(verts_bytes, len(verts))

    tri_bytes = b''
    
    # Pack all the triangles
    for tri in tris:

        tri_bytes += struct.pack('<HHH', *tri)

    # Add a length prefix indicating the number of triangle indices 
    tri_bytes = add_length(tri_bytes, len(tris) * 3)
    
    return verts_bytes + tri_bytes

def pack_single_quad(quad: Tuple[Tuple[float, float]]) -> bytes:

    '''
    Pack a single quad element into a bytes object 
    '''

    # Emulate the 1, 0, 0, 1 pattern, and just assume zeros for the weirdo altitude field

    return struct.pack('<' + 'fffff' * 4,
            quad[0][0], 0, quad[0][1], 0, 1,
            quad[1][0], 0, quad[1][1], 0, 0,
            quad[2][0], 0, quad[2][1], 0, 0,
            quad[3][0], 0, quad[3][1], 0, 1
        )

def pack_quads(quad_list: List[Tuple[Tuple[float, float]]]) -> bytes:

    '''
    Pack a list of quads into a single bytes object
    '''

    output_bytes = b''

    for quad in quad_list:

        output_bytes += pack_single_quad(quad)
    
    return add_length(output_bytes, len(quad_list) * 4)