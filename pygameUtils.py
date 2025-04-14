import math
import pygame

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
    
    rect_width = thickness
    rect_height = length
    rect = pygame.Rect(0, 0, rect_width, rect_height)
    
    rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    rect_surface.fill((0, 0, 0, 0)) 
    pygame.draw.rect(rect_surface, color, (0, 0, rect_width, rect_height),border_radius=5)

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