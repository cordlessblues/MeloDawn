import pygame
import math
import time
import collections

class TouchInput:
    def __init__(self, surface):
        self.surface = surface
        self.fingers = {}
        self.prev_positions = {}
        self.gestures = []
        self.rotation = 0.0
        self.pinch = 0.0
        self.last_taps = []
        self.active_swipes = {}
        self.swipe_counts = {}
        self.debug_enabled = True
        self.swipe_threshold = 1

    def update(self, events):
        self.gestures.clear()
        self.rotation = 0.0
        self.pinch = 0.0

        for e in events:
            if e.type == pygame.FINGERDOWN:
                now = time.time()
                self.fingers[e.finger_id] = (e.x, e.y)
                self.prev_positions[e.finger_id] = (e.x, e.y)
                self.active_swipes[e.finger_id] = [(e.x, e.y)]
                self.swipe_counts[e.finger_id] = collections.Counter()
                if self.last_taps and now - self.last_taps[-1][0] < 0.35:
                    _, last_pos = self.last_taps[-1]
                    dx = e.x - last_pos[0]; dy = e.y - last_pos[1]
                    if dx*dx + dy*dy < 0.05**2:
                        self.gestures.append("double_tap")
                        self.last_taps.clear()
                self.last_taps.append((now, (e.x, e.y)))

            elif e.type == pygame.FINGERMOTION:
                prev = self.fingers.get(e.finger_id, (e.x, e.y))
                self.prev_positions[e.finger_id] = prev
                self.fingers[e.finger_id] = (e.x, e.y)
                path = self.active_swipes.setdefault(e.finger_id, [])
                path.append((e.x, e.y))
                dir = self._swipe_direction(prev, (e.x, e.y))
                if dir:
                    self.swipe_counts[e.finger_id][dir] += 1

            elif e.type == pygame.FINGERUP:
                counter = self.swipe_counts.pop(e.finger_id, None)
                if counter:
                    most = counter.most_common(1)
                    if most and most[0][1] > 0:
                        direction = most[0][0]
                        self.gestures.append(f"swipe_{direction}")
                self.prev_positions.pop(e.finger_id, None)
                self.fingers.pop(e.finger_id, None)
                self.active_swipes.pop(e.finger_id, None)

        multi_swipe = any(g.startswith("swipe_") for g in self.gestures)

        if not multi_swipe:
            if len(self.fingers) >= 3:
                delta = self._calculate_rotation()
                self.rotation = delta
                if abs(delta) > 0.05:
                    self.gestures.append('rotate_cw' if delta > 0 else 'rotate_ccw')

        if len(self.fingers) >= 2:
            pinch_change = self._calculate_pinch()
            if abs(pinch_change) > 0.01:
                self.pinch = pinch_change
                self.gestures.append('pinch_out' if pinch_change > 0 else 'pinch_in')

    def _swipe_direction(self, start, end):
        w, h = self.surface.get_size()
        sx, sy = start[0] * w, start[1] * h
        ex, ey = end[0] * w, end[1] * h
        dx, dy = ex - sx, ey - sy
        if math.hypot(dx, dy) < self.swipe_threshold:
            return None
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'

    def _calculate_rotation(self):
        pts = list(self.fingers.values())
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        total, count = 0, 0
        for fid, new in self.fingers.items():
            old = self.prev_positions.get(fid)
            if not old:
                continue
            a1 = math.atan2(old[1] - cy, old[0] - cx)
            a2 = math.atan2(new[1] - cy, new[0] - cx)
            d = a2 - a1
            while d > math.pi:
                d -= 2 * math.pi
            while d < -math.pi:
                d += 2 * math.pi
            total += d
            count += 1
        return total / count if count else 0.0

    def _calculate_pinch(self):
        old_dists, new_dists = [], []
        ids = list(self.fingers.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                id1, id2 = ids[i], ids[j]
                if id1 in self.prev_positions and id2 in self.prev_positions:
                    old1, old2 = self.prev_positions[id1], self.prev_positions[id2]
                    new1, new2 = self.fingers[id1], self.fingers[id2]
                    old_dist = math.hypot(old2[0] - old1[0], old2[1] - old1[1])
                    new_dist = math.hypot(new2[0] - new1[0], new2[1] - new1[1])
                    old_dists.append(old_dist)
                    new_dists.append(new_dist)
        if not old_dists:
            return 0.0
        avg_old = sum(old_dists) / len(old_dists)
        avg_new = sum(new_dists) / len(new_dists)
        return avg_new - avg_old

    def draw_debug(self):
        if not self.debug_enabled:
            return
        for path in self.active_swipes.values():
            if len(path) > 1:
                pts = [(x * self.surface.get_width(), y * self.surface.get_height()) for x, y in path]
                pygame.draw.lines(self.surface, (255, 255, 0), False, pts, 3)
        if self.rotation and self.fingers:
            pts = list(self.fingers.values())
            cx = sum(x for x, y in pts) / len(pts)
            cy = sum(y for x, y in pts) / len(pts)
            pygame.draw.circle(
                self.surface,
                (255, 0, 255),
                (
                    int(cx * self.surface.get_width()),
                    int(cy * self.surface.get_height())
                ),
                12,
                2
            )
        if self.pinch and self.fingers:
            pts = list(self.fingers.values())
            cx = sum(x for x, y in pts) / len(pts)
            cy = sum(y for x, y in pts) / len(pts)
            r = 30 + int(self.pinch * 300)
            pygame.draw.circle(
                self.surface,
                (0, 255, 255),
                (
                    int(cx * self.surface.get_width()),
                    int(cy * self.surface.get_height())
                ),
                abs(r),
                2
            )
        for g in self.gestures:
            if g == 'double_tap':
                pygame.draw.circle(self.surface, (0, 0, 255), (100, 100), 20)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    touch = TouchInput(screen)
    touch.debug_enabled = True
    running = True
    while running:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
        touch.update(events)
        for gesture in touch.gestures:
            print('Gesture detected:', gesture)
        screen.fill((30, 30, 30))
        touch.draw_debug()
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
