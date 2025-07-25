def scale_path(path, scale):

    output_path = []

    for item in path:

        new_item = []

        for coord in item:

            new_item.append((coord[0] * scale, coord[1] * scale))
        
        output_path.append(new_item)
    
    return output_path

def offset_path(path, offset_x, offset_y):

    output_path = []

    for item in path:

        new_item = []

        for coord in item:

            new_item.append((coord[0] + offset_x, coord[1] + offset_y))
        
        output_path.append(new_item)

    return output_path