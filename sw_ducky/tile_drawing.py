from PIL import Image, ImageDraw
from PIL.Image import Image as PILImage
from PIL.ImageDraw import ImageDraw as PILImageDraw
from typing import Tuple, List

def draw_dashed_line(
    draw: PILImageDraw,
    start: Tuple[float, float],
    end: Tuple[float, float],
    dash_length: float = 10,
    gap: float = 5,
    **kwargs
) -> None:
    '''
    Draw a dashed line between two points.
    '''
    from math import hypot

    # Determine some constants related to the line
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    dist = hypot(dx, dy)

    # Calculate the number of steps required
    steps = int(dist // (dash_length + gap))

    # Iterate over each step
    for i in range(steps + 1):

        # Determine what fraction of the line we are through it
        start_frac = i * (dash_length + gap) / dist
        end_frac = min(start_frac + dash_length / dist, 1.0)

        # Calculate the x,y coordinates of the current dash
        sx = x1 + dx * start_frac
        sy = y1 + dy * start_frac
        ex = x1 + dx * end_frac
        ey = y1 + dy * end_frac

        # Draw the dash
        draw.line([(sx, sy), (ex, ey)], **kwargs)


def convert_axis_value(size: int, value: float, flip: bool = False) -> float:
    '''
    Convert a coordinate from range [-500, 500] to [0, size].
    '''
    if flip:
        return size - (size * ((value + 500) / 1000))
    return size * ((value + 500) / 1000)


def convert_coord(size: int, coord: Tuple[float, float]) -> Tuple[float, float]:
    '''
    Convert a 2D coordinate to image space.
    '''
    return (
        convert_axis_value(size, coord[0]),
        convert_axis_value(size, coord[1], flip=True)
    )


def convert_coords(size: int, coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    '''
    Convert a list of 2D coordinates to image space.
    '''
    return [convert_coord(size, c) for c in coords]


class TileCanvas:
    '''
    A simple canvas that allows drawing triangles and lines onto a tile image.
    '''

    def __init__(self, size: int, back_color: Tuple[int, int, int]):
        self.tile_img: PILImage = Image.new('RGB', (size, size), back_color)
        self.tile_draw: PILImageDraw = ImageDraw.Draw(self.tile_img)
        self.size: int = size

    def triangle(self, coords: List[Tuple[float, float]], color: Tuple[int, int, int]) -> None:
        '''
        Draw a filled triangle on the canvas.
        '''
        self.tile_draw.polygon(convert_coords(self.size, coords), fill=color)

    def draw_line(
        self,
        cord_1: Tuple[float, float],
        cord_2: Tuple[float, float],
        color: Tuple[int, int, int],
        dashed: bool = False
    ) -> None:
        '''
        Draw a line on the canvas, optionally dashed.
        '''
        converted_cord_1 = convert_coord(self.size, cord_1)
        converted_cord_2 = convert_coord(self.size, cord_2)

        if dashed:
            draw_dashed_line(
                self.tile_draw,
                converted_cord_1,
                converted_cord_2,
                fill=color,
                width=2,
                dash_length=4,
                gap=4
            )
        else:
            self.tile_draw.line(
                [converted_cord_1, converted_cord_2],
                fill=color,
                width=2
            )
