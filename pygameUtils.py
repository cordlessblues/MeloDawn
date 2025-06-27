import math
import pygame
import PIL 
from pygame import gfxdraw
from PIL import Image
from PIL import ImageFilter
from ColorUtils import *

def get_points_on_edge(x, y, s, r, points_per_side, points_per_corner):
    Output = []

    # Top edge
    for i in range(points_per_side):
        x_top = x + r + (i / (points_per_side - 1)) * (s - 2 * r)
        y_top = y
        Output.append((int(x_top), int(y_top)))

    # Top-right corner 
    for i in range(1, points_per_corner - 1):
        angle = 1.5 * math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + s - r + r * math.cos(angle)
        y_corner = y + r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Right edge
    for i in range(points_per_side):
        x_right = x + s
        y_right = y + r + (i / (points_per_side - 1)) * (s - 2 * r)
        Output.append((int(x_right), int(y_right)))

    # Bottom-right corner 
    for i in range(1, points_per_corner - 1):
        angle = 0 * math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + s - r + r * math.cos(angle)
        y_corner = y + s - r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Bottom edge 
    for i in range(points_per_side):
        x_bottom = x + s - r - (i / (points_per_side - 1)) * (s - 2 * r)
        y_bottom = y + s
        Output.append((int(x_bottom), int(y_bottom)))

    # Bottom-left corner 
    for i in range(1, points_per_corner - 1):
        angle = 0.5 * math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + r + r * math.cos(angle)
        y_corner = y + s - r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Left edge 
    for i in range(points_per_side):
        x_left = x
        y_left = y + s - r - (i / (points_per_side - 1)) * (s - 2 * r)
        Output.append((int(x_left), int(y_left)))

    # Top-left corner 
    for i in range(1, points_per_corner - 1):
        angle = math.pi + (i / (points_per_corner - 1)) * (0.5 * math.pi)
        x_corner = x + r + r * math.cos(angle)
        y_corner = y + r + r * math.sin(angle)
        Output.append((int(x_corner), int(y_corner)))

    # Remove duplicates

    return Output

def draw_rounded_rect_line(surface, color, start_pos, end_pos, radius, thickness):
    angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0]) + math.pi / 2
    
    length = math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
    
    rect_width = int(thickness)
    rect_height = int(length)
    
    rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    rect_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(rect_surface, color,(0, 0, rect_width, rect_height),border_radius=int(radius))

    rotated_rect = pygame.transform.rotate(rect_surface, -math.degrees(angle))
    
    new_rect = rotated_rect.get_rect(center=((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2))

    surface.blit(rotated_rect, new_rect.topleft)

def CalculateLineThickness(current_second, max_value=255, num_lines=60):
    Values = []
    
    for i in range(num_lines):
        # Calculate the distance from the current second
        offset_index = (i - current_second) % num_lines  # Offset based on current second
        value = (offset_index / (num_lines - 1)) * max_value  # Scale from 0 to max_value
        Values.append(value)
    
    return Values

def Bloom(blurSize: int, surface: pygame.Surface):
    width, height = surface.get_size()
    small_size = (width // 2, height // 2)

    # Scale down the surface for faster blur processing
    resized = pygame.transform.smoothscale(surface, small_size)

    # Convert to a string of bytes
    img_str = pygame.image.tostring(resized, "RGBA", False)

    # Create a PIL image from the byte string, using the correct size
    im = Image.frombytes("RGBA", small_size, img_str)

    # Apply Gaussian blur using PIL
    im = im.filter(ImageFilter.GaussianBlur(blurSize))

    # Convert the blurred PIL image back to bytes
    blurred_str = im.tobytes()

    # Create a new Pygame surface from the blurred bytes
    blurred_surface = pygame.image.fromstring(blurred_str, small_size, "RGBA")

    # Scale the blurred surface back up to the original size
    final = pygame.transform.smoothscale(blurred_surface, (width, height))

    # Blend the blurred image back onto the original surface using additive blending
    surface.blit(final, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

_circle_cache = {}
def add_outline_to_image(self,image: pygame.Surface, thickness: int, color: tuple, color_key: tuple = (255, 0, 255)) -> pygame.Surface:
    mask = pygame.mask.from_surface(image)
    mask_surf = mask.to_surface(setcolor=color)
    mask_surf.set_colorkey((0, 0, 0))
    new_img = pygame.Surface((image.get_width() + 2, image.get_height() + 2))
    new_img.fill(color_key)
    new_img.set_colorkey(color_key)
    for i in -thickness, thickness:
        new_img.blit(mask_surf, (i + thickness, thickness))
        new_img.blit(mask_surf, (thickness, i + thickness))
    new_img.blit(image, (thickness, thickness))
    return new_img

def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points

def render_outline_text(text, font, text_color, outline_color, outline_thickness):
    """Render text with an outline."""
    # Render the main text
    text_surface = font.render(text, True, text_color)
    w = text_surface.get_width() + 2 * outline_thickness
    h = font.get_height() + 2 * outline_thickness
    # Create surface for the outlined text
    outline_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    # Render the outline
    base_outline = font.render(text, True, outline_color)
    for dx, dy in _circlepoints(outline_thickness):
        outline_surface.blit(base_outline, (dx + outline_thickness, dy + outline_thickness))
    # Render the main text on top
    outline_surface.blit(text_surface, (outline_thickness, outline_thickness))
    return outline_surface

def render_text_with_outline(text, font, text_color, outline_color, outline_thickness):
    # Step 1: Render the text normally
    text_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)
    
    # Step 2: Create a mask from the outline surface
    mask = pygame.mask.from_surface(outline_surface)
    
    # Step 3: Create a surface for the outline
    outline_surf = pygame.Surface((text_surface.get_width() + outline_thickness * 2, 
                                   text_surface.get_height() + outline_thickness * 2), pygame.SRCALPHA)
    outline_surf.fill((0, 0, 0, 0))  # Transparent background
    
    # Step 4: Apply the mask to create the outline effect
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            outline_surf.blit(outline_surface, (dx, dy), special_flags=pygame.BLEND_RGBA_ADD)
    
    # Step 5: Blit the original text on top of the outline
    outline_surf.blit(text_surface, (outline_thickness, outline_thickness))

    return outline_surf


class InterpolatedValue():
    def __init__(self, currentValue: int | float, targetValue: int | float, totalTime: int | float):
        self.startValue = currentValue  
        self.currentValue = currentValue
        self.targetValue = targetValue
        self.elapsedTime = 0.0          
        self.totalTime = float(totalTime) 

        
        if self.totalTime <= 0:
            self.currentValue = self.targetValue 
            self.elapsedTime = self.totalTime

    def update(self, deltaTime: int | float):
        if self.elapsedTime < self.totalTime:
            self.elapsedTime += float(deltaTime)

            self.elapsedTime = min(self.elapsedTime, self.totalTime)

            progress = self.elapsedTime / self.totalTime

            #linear interp
            self.currentValue = self.startValue + (self.targetValue - self.startValue) * progress

    def set_target(self,val):
        self.startValue = self.currentValue
        self.elapsedTime = 0.0
        self.targetValue = val
        
    
    def is_finished(self) -> bool:
        return self.elapsedTime >= self.totalTime

    #override float
    def __int__(self) -> int:
        return int(self.currentValue)
    
    #override float
    def __float__(self) -> float:
        return float(self.currentValue)

    #override str
    def __str__(self) -> str:
        return str(self.currentValue)

    #override print() output
    def __repr__(self) -> str:
        return f"InterpolatedValue(currentValue={self.currentValue},targetValue={self.targetValue}, elapsedTime={self.elapsedTime}, totalTime={self.totalTime})"