from typing import List, Tuple

def scale_path(path: List[Tuple[Tuple[float, float]]], scale: float) -> List[Tuple[Tuple[float, float]]]:

    '''
    Scale a path by a scalar amount
    '''

    output_path = []

    for item in path:

        new_item = []

        for coord in item:

            new_item.append((coord[0] * scale, coord[1] * scale))
        
        output_path.append(new_item)
    
    return output_path

def offset_path(path: List[Tuple[Tuple[float, float]]], offset_x: float, offset_y: float) -> List[Tuple[Tuple[float, float]]]:

    '''
    Offset a path by a certain X,Y amount
    '''

    output_path = []

    for item in path:

        new_item = []

        for coord in item:

            new_item.append((coord[0] + offset_x, coord[1] + offset_y))
        
        output_path.append(new_item)

    return output_path