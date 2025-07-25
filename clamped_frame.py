from math import inf
import pygame
import pygame.gfxdraw
import time

pygame.init()

def remap_framing(min_from_range, max_from_range, min_to_range, max_to_range, value):

    # First cast to the range 0 -> 1
    normed_value = (value - min_from_range) / (max_from_range - min_from_range)

    # Now convert to the new range
    return normed_value * (max_to_range - min_to_range) + min_to_range

class Frame:
    def __init__(self, size_x, size_y, frame_min_x, frame_max_x, frame_min_y, frame_max_y, margin = 1.3, fps = 30):
        self.size_x = size_x
        self.size_y = size_y
        self.frame_min_x = frame_min_x
        self.frame_max_x = frame_max_x
        self.frame_min_y = frame_min_y
        self.frame_max_y = frame_max_y

        self.screen = pygame.display.set_mode((size_x, size_y))
        self.line_surface = pygame.Surface((size_x, size_y), pygame.SRCALPHA)


        self.cached_draw_commands = []
        self.polygon_draw_commands = []

        self.margin = margin

        # Check aspect ratio

        aspect_ratio_x = (frame_max_x - frame_min_x) / size_x
        aspect_ratio_y = (frame_max_y - frame_min_y) / size_y

        comparison = aspect_ratio_x / aspect_ratio_y

        if comparison < 1:
            comparison = 1 / comparison

        if comparison > 1 + 1e-1:
            print('WARN: Inconsistent aspect ratio')
        
        self.t = time.time()
        self.fps = fps

    def line(self, from_cord, to_cord, color, adjust_framing = True):
        self.cached_draw_commands.append((from_cord, to_cord, color, adjust_framing))
    
    def polygon(self, coords, color, frame = True):
        self.polygon_draw_commands.append((coords, color, frame))

    def render_path(self, path, color, loop = True, frame = True):

        cached_cord = None

        if len(path) <= 1:
            return

        for new_cord in path:

            if cached_cord is not None:

                self.line(cached_cord, new_cord, color, adjust_framing = frame)

            cached_cord = new_cord
        
        if loop:
            self.line(cached_cord, path[0], color, adjust_framing = frame)

    def update(self):

        self.line_surface.fill((40, 100, 110))

        # First define current framing
        calculated_min_x = inf
        calculated_min_y = inf
        calculated_max_x = -inf
        calculated_max_y = -inf

        def single_dimension_framing(c_min, c_max, v):
            if v < c_min:
                c_min = v
            
            if v > c_max:
                c_max = v
            
            return c_min, c_max

        for c1, c2, _, adj_framing in self.cached_draw_commands:

            if not adj_framing:
                continue

            calculated_min_x, calculated_max_x = single_dimension_framing(calculated_min_x, calculated_max_x, c1[0])
            calculated_min_y, calculated_max_y = single_dimension_framing(calculated_min_y, calculated_max_y, c1[1])
            calculated_min_x, calculated_max_x = single_dimension_framing(calculated_min_x, calculated_max_x, c2[0])
            calculated_min_y, calculated_max_y = single_dimension_framing(calculated_min_y, calculated_max_y, c2[1])

        for coords, _, adj_framing in self.polygon_draw_commands:

            if not adj_framing:
                continue

            for x, y in coords:
                calculated_min_x, calculated_max_x = single_dimension_framing(calculated_min_x, calculated_max_x, x)
                calculated_min_y, calculated_max_y = single_dimension_framing(calculated_min_y, calculated_max_y, y)

        # Apply margin to calculated bounds
        center_x = (calculated_max_x + calculated_min_x) / 2
        center_y = (calculated_max_y + calculated_min_y) / 2
        width_x = (calculated_max_x - calculated_min_x)
        height_y = (calculated_max_y - calculated_min_y)

        width_x *= self.margin
        height_y *= self.margin

        calculated_max_x = center_x + (width_x / 2)
        calculated_min_x = center_x - (width_x / 2)
        calculated_max_y = center_y + (height_y / 2)
        calculated_min_y = center_y - (height_y / 2)

        frame_min_x = min(self.frame_min_x, calculated_min_x)
        frame_max_x = max(self.frame_max_x, calculated_max_x)
        frame_min_y = min(self.frame_min_y, calculated_min_y)
        frame_max_y = max(self.frame_max_y, calculated_max_y)

        # Now that we have determined the optimal framing, we now correct the frame to have the correct aspect ratio
        f_x_ratio = (frame_max_x - frame_min_x) / (self.frame_max_x - self.frame_min_x)
        f_y_ratio = (frame_max_y - frame_min_y) / (self.frame_max_y - self.frame_min_y)

        if f_x_ratio > f_y_ratio:
            # We need to add a bit onto the y range

            ratio_delta = f_x_ratio - f_y_ratio
            increase_by = ratio_delta * (self.frame_max_y - self.frame_min_y)
            increase_by /= 2
            frame_min_y -= increase_by
            frame_max_y += increase_by

        if f_y_ratio > f_x_ratio:
            # We need to add a bit onto the x range

            ratio_delta = f_y_ratio - f_x_ratio
            increase_by = ratio_delta * (self.frame_max_x - self.frame_min_x)
            increase_by /= 2
            frame_min_x -= increase_by
            frame_max_x += increase_by


        def remap_single_dim(min_val, max_val, min_target, max_target, value):

            if value == -inf:
                return min_target
            
            if value == inf:
                return max_target
            
            return round(remap_framing(min_val, max_val, min_target, max_target, value))

        # Now we can execute the draw commands
        try:
            for coords, color, _ in self.polygon_draw_commands:

                filtered_coords = [
                    (
                        remap_single_dim(frame_min_x, frame_max_x, 0, self.size_x, x),
                        remap_single_dim(frame_min_y, frame_max_y, self.size_y, 0, y)
                    )
                    for x, y in coords
                ]

                pygame.draw.polygon(self.line_surface, color, filtered_coords)
        except:
            for coords, color, _ in self.polygon_draw_commands:

                for x, y in coords:
                    try:
                        remap_single_dim(frame_min_x, frame_max_x, 0, self.size_x, x),
                        remap_single_dim(frame_min_y, frame_max_y, self.size_y, 0, y)
                    except:
                        ValueError(coords)
        

        for c1, c2, color, _ in self.cached_draw_commands:

            c1_x = remap_single_dim(frame_min_x, frame_max_x, 0, self.size_x, c1[0])
            c1_y = remap_single_dim(frame_min_y, frame_max_y, self.size_y, 0, c1[1])
            c2_x = remap_single_dim(frame_min_x, frame_max_x, 0, self.size_x, c2[0])
            c2_y = remap_single_dim(frame_min_y, frame_max_y, self.size_y, 0, c2[1])

            pygame.gfxdraw.line(self.line_surface, c1_x, c1_y, c2_x, c2_y, color)
            pygame.draw.line(self.line_surface, color, (c1_x, c1_y), (c2_x, c2_y), 2)
    
        self.screen.blit(self.line_surface, (0, 0))  # Blit with blending
        pygame.display.flip()

        pygame.display.flip()
        events = pygame.event.get()

        for ev in events:
            if ev.type == pygame.QUIT:
                exit()

        self.cached_draw_commands.clear()
        self.polygon_draw_commands.clear()

        current_time = time.time()

        delay_time = (1 / self.fps) - (current_time - self.t)

        t = time.time()

        while time.time() - t < delay_time:
            events = pygame.event.get()

            for ev in events:
                if ev.type == pygame.QUIT:
                    exit()

        self.t = time.time()