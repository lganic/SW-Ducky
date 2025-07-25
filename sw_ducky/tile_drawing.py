from PIL import Image, ImageDraw

def draw_dashed_line(draw, start, end, dash_length=10, gap=5, **kwargs):
    from math import hypot
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    dist = hypot(dx, dy)
    steps = int(dist // (dash_length + gap))
    for i in range(steps + 1):
        start_frac = i * (dash_length + gap) / dist
        end_frac = min(start_frac + dash_length / dist, 1.0)
        sx = x1 + dx * start_frac
        sy = y1 + dy * start_frac
        ex = x1 + dx * end_frac
        ey = y1 + dy * end_frac
        draw.line([(sx, sy), (ex, ey)], **kwargs)

def convert_axis_value(size, value, flip = False):

    # Remap a value from the range -500 -> 500 to the range 0 -> size

    if flip:
        return size - (size * ((value + 500) / 1000))
    
    return size * ((value + 500) / 1000)

def convert_coord(size, coord):

    return (convert_axis_value(size, coord[0]), convert_axis_value(size, coord[1], flip = True))

def convert_coords(size, coords):

    return [convert_coord(size, c) for c in coords]

class TileCanvas:

    def __init__(self, size, back_color):
        
        self.tile_img = Image.new('RGB', (size, size), back_color)
        self.tile_draw = ImageDraw.Draw(self.tile_img)

        self.size = size
    
    def triangle(self, coords, color):

        self.tile_draw.polygon(convert_coords(self.size, coords), fill = color)
    
    def draw_line(self, cord_1, cord_2, color, dashed = False):

        converted_cord_1 = convert_coord(self.size, cord_1)
        converted_cord_2 = convert_coord(self.size, cord_2)

        if dashed:
            draw_dashed_line(self.tile_draw, converted_cord_1, converted_cord_2, fill=color, width=2, dash_length=4, gap = 4)

        else:
            self.tile_draw.line([converted_cord_1, converted_cord_2], fill=color, width=2)
