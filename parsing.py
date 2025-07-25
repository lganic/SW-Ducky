import struct

from utilitity import is_cord_valid, is_poly_valid

def read_single_mesh_chunk(bin, index):

    chunk_length = struct.unpack('<H', bin[index: index + 2])[0]

    read_index = 2 + index

    coordinates = []

    for _ in range(chunk_length):

        coordinate = struct.unpack('<fff', bin[read_index: read_index + 12])

        x, _, y = coordinate

        if not is_cord_valid((x, y)):
            # Coordinate had some invalid entries. 

            raise ValueError(f'An invalid coordinate was read from the file: {(x, y)} at index: {read_index}')

        read_index += 12

        coordinates.append((x, y))

    edges_chunk_length = struct.unpack('<H', bin[read_index: read_index + 2])[0]

    tris = []

    read_index += 2

    for _ in range(edges_chunk_length // 3):

        edges = struct.unpack('<HHH', bin[read_index: read_index + 6])

        read_index += 6

        tris.append(edges)

    return (coordinates, tris), read_index - index

def read_line_quads(bin, index):

    chunk_length = struct.unpack('<H', bin[index: index + 2])[0]

    part_index = 2 + index

    quads = []

    for _ in range(chunk_length // 4):

        (
            x1, _, y1, _alt1, _one_or_zero,
            x2, _, y2, _alt2, _one_or_zero,
            x3, _, y3, _alt3, _one_or_zero,
            x4, _, y4, _alt4, _one_or_zero
        ) = struct.unpack('<' + 'fffIf' * 4, bin[part_index : part_index + 80])

        print(_alt1, _alt2, _alt3, _alt4)

        part_index += 80

        quad = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))

        if not is_poly_valid(quad):
            # This happens from time to time, likely due to SW devs shitty dev codebase. We can safely ignore these packets though, because of the way that the later rendering works.
            continue

        quads.append(quad)
    
    return quads, part_index - index

def read_n_using_func(bin, index, number, function):

    part_index = index

    results = []

    for _ in range(number):

        result, offset = function(bin, part_index)

        results.append(result)

        part_index += offset
    
    return results, part_index - index

def add_length(byte_string, value):

    length_bytes = struct.pack('<H', value)

    return length_bytes + byte_string
    

def pack_single_mesh(verts, tris):

    verts_bytes = b''

    for vert in verts:

        verts_bytes += struct.pack('<fff', vert[0], 0, vert[1])

    verts_bytes = add_length(verts_bytes, len(verts))

    tri_bytes = b''
    
    for tri in tris:

        tri_bytes += struct.pack('<HHH', *tri)

    tri_bytes = add_length(tri_bytes, len(tris) * 3)
    
    return verts_bytes + tri_bytes

def pack_single_quad(quad):

    return struct.pack('<' + 'fffIf' * 4,
            quad[0][0], 0, quad[0][1], 1110254360, 1,
            quad[1][0], 0, quad[1][1], 1110254360, 0,
            quad[2][0], 0, quad[2][1], 1110254360, 0,
            quad[3][0], 0, quad[3][1], 1110254360, 1
        )

def pack_quads(quad_list):

    output_bytes = b''

    for quad in quad_list:

        output_bytes += pack_single_quad(quad)
    
    return add_length(output_bytes, len(quad_list) * 4)