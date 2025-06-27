import pygame

class Widget:
    def __init__(self, baseRes: int):
        self.baseRes = baseRes
        self.scaleFactor = baseRes / 1024.0  # Use float for scaling
        self.isVisible = True
        self.renderSurface: pygame.surface.Surface = None  # To be created by subclasses
        self.rect = pygame.Rect(0, 0, 0, 0)  # To store the widget's position and size
        self.dirtyRects = []
        self.LowLightActive = False

    def NeedsUpdate(self):
        return True
    
    def update(self, delta_time: float):
        """
        Update the widget's internal state.
        This method should be overridden by subclasses.
        """
        pass

    def render(self, screen: pygame.surface.Surface, rect: pygame.Rect):
        """
        Render the widget onto the screen.
        This method should be overridden by subclasses to draw specific content.
        """
        self.rect = rect  # Update the widget's position and size

        # Check if the widget's rectangle overlaps with the screen's rectangle
        self.isVisible = self.rect.colliderect(screen.get_rect())

        if self.isVisible and self.renderSurface:
            # Scale the widget's surface to match the target rect size
            if self.renderSurface.get_size() == rect.size:
                # If the render surface is the same size as the widget rect, no scaling needed
                screen.blit(self.renderSurface, rect)
            else:
                # Create a new surface with the target dimensions for scaling
                scaled_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

                # Scale the contents of the widget's render_surface onto the scaled_surface.
                pygame.transform.smoothscale(self.renderSurface, (rect.width, rect.height), scaled_surface)

                # Blit the scaled_surface onto the main Screen at the specified position (rect).
                screen.blit(scaled_surface, rect)

    def getDirtyRects(self, rect: pygame.Rect):
        """
        Convert local widget dirty rects into global screen coordinates and merge adjacent rects.
        """
        scaled_dirty_rects = []
        for dirty_rect in self.dirtyRects:
            scaled_rect = pygame.Rect(
                rect.x + (dirty_rect.x * rect.width / self.renderSurface.get_width()),
                rect.y + (dirty_rect.y * rect.height / self.renderSurface.get_height()),
                dirty_rect.width * rect.width / self.renderSurface.get_width(),
                dirty_rect.height * rect.height / self.renderSurface.get_height()
            )
            scaled_dirty_rects.append(scaled_rect)
    
        # Merge overlapping or adjacent rects
        if len(scaled_dirty_rects) > 1:
            scaled_dirty_rects = self.mergeRects(scaled_dirty_rects)
    
        return scaled_dirty_rects

    def mergeRects(self, rects):
        """
        Merge overlapping or adjacent rectangles into one larger rectangle.
        """
        # Sort rects by their x position, then by their y position
        rects.sort(key=lambda r: (r.x, r.y))
        merged = []

        for rect in rects:
            if not merged:
                merged.append(rect)
            else:
                last_rect = merged[-1]
                if last_rect.colliderect(rect) or last_rect.right >= rect.left - 1:
                    # Merge rectangles if they overlap or are adjacent (1px tolerance)
                    merged[-1] = last_rect.union(rect)
                else:
                    # Otherwise, just add the current rectangle as-is
                    merged.append(rect)

        return merged

