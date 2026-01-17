import time
import math
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

# ---------------------------
# Constants & Globals
# ---------------------------
# Game
current_level = 1
player_lives = 4
max_lives = 4

game_start_time = 0
level_start_time = None
level_play_accum = 0.0

portals_used = 0
shots_fired = 0
shots_hit = 0
game_score = 0
game_over = False
level_complete = False
paused = False
cheat_mode = False

# Player / Camera
player_pos = [10.0, 0.0, 10.0]  # spawn in the center
player_yaw = 0.0
player_pitch = 0.0
cam_speed = 0.5
yaw_speed = 6
v_y = 0.0
GRAVITY = -20.0
is_falling = False

# World
room_size = 20.0
wall_tiles = []  # list of [coords, color]

# Bullets & Portals
bullets = []
BULLET_SPEED = 7.0
BULLET_LIFETIME = 5.0
BULLET_RADIUS = 0.1

portals = []
tile_portal_map = {}
_next_portal_id = 1

# Button / Door
BUTTON_POS = [2, 0, 2]
BUTTON_RADIUS = 2
BUTTON_HEIGHT = 0.833
door_color = 'red'
button_activated = False

# Moving obstacles & horizontal lasers
moving_obstacles = []
OBSTACLE_SPEED = 3.0

horizontal_lasers = []  # list of laser dicts

# Timing / input
last_frame_time = time.time()
last_teleport_time = 0.0
TELEPORT_COOLDOWN = 1.0

mouse_captured = False
window_width = 800
window_height = 600

MAX_LEVEL = 5  # total levels

# Colors (template palette)
BG_COLOR = (0.05, 0.05, 0.15)
FLOOR_COLOR = (0.1, 0.1, 0.2)
CEILING_COLOR = (0.15, 0.1, 0.25)
WALL_COLOR = (0.2, 0.15, 0.3)
WALL_EDGE_COLOR = (1.0, 1.0, 1.0)
PORTAL_BLUE = (0.0, 1.0, 1.0)
PORTAL_YELLOW = (1.0, 1.0, 0.0)
BUTTON_COLOR = (0.0, 1.0, 0.0)
LASER_COLOR = (1.0, 0.0, 0.0)
DOOR_RED = (1.0, 0.0, 0.0)
DOOR_GREEN = (0.0, 1.0, 0.0)

# ---------------------------
# Small helpers
# ---------------------------


def clamp(v, a, b):
    return max(a, min(b, v))


def now():
    return time.time()


def min_max_coords(coords):
    """Return (x_min, x_max, y_min, y_max, z_min, z_max) for a quad."""
    xs = [v[0] for v in coords]
    ys = [v[1] for v in coords]
    zs = [v[2] for v in coords]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _scale_color(color, factor):
    """Scale RGB tuple while clamping to [0,1]."""
    return (
        clamp(color[0] * factor, 0.0, 1.0),
        clamp(color[1] * factor, 0.0, 1.0),
        clamp(color[2] * factor, 0.0, 1.0),
    )


def _point_in_aabb(p, aabb_min, aabb_max):
    x, y, z = p
    return (aabb_min[0] <= x <= aabb_max[0] and
            aabb_min[1] <= y <= aabb_max[1] and
            aabb_min[2] <= z <= aabb_max[2])


def _find_portal_by_id(pid):
    for p in portals:
        if p['id'] == pid:
            return p
    return None


# ---------------------------
# Portal management
# ---------------------------


def _remove_portal(portal_id):
    """Remove a portal and clear mapping and partner link."""
    global portals, tile_portal_map
    p = _find_portal_by_id(portal_id)
    if not p:
        return
    # unpair partner if present
    if p['paired_with'] is not None:
        partner = _find_portal_by_id(p['paired_with'])
        if partner:
            partner['paired_with'] = None
    t = p['tile_index']
    if tile_portal_map.get(t) == portal_id:
        tile_portal_map.pop(t, None)
    portals[:] = [q for q in portals if q['id'] != portal_id]
    if 0 <= t < len(wall_tiles):
        wall_tiles[t][1] = 'gray'


def _place_portal_on_tile(tile_index, color):
    """
    Place a portal on tile_index with color 'blue' or 'yellow'.
    If the opposite unpaired portal exists, pair them.
    """
    global _next_portal_id, portals, tile_portal_map
    existing_id = tile_portal_map.get(tile_index)
    if existing_id is not None:
        _remove_portal(existing_id)

    pid = _next_portal_id
    _next_portal_id += 1
    portal_obj = {'id': pid, 'color': color,
                  'tile_index': tile_index, 'paired_with': None}
    portals.append(portal_obj)
    tile_portal_map[tile_index] = pid

    # pair with the first unpaired opposite (search reversed to prefer recent)
    opposite = 'yellow' if color == 'blue' else 'blue'
    for p in reversed(portals):
        if p['color'] == opposite and p['paired_with'] is None and p['id'] != pid:
            portal_obj['paired_with'] = p['id']
            p['paired_with'] = portal_obj['id']
            break

    if 0 <= tile_index < len(wall_tiles):
        wall_tiles[tile_index][1] = color

    return portal_obj


def any_unpaired(color):
    for p in portals:
        if p['color'] == color and p['paired_with'] is None:
            return True
    return False


# ---------------------------
# Drawing helpers
# ---------------------------


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Simple 2D text using orthographic projection."""
    glColor3f(1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_hud():
    """HUD positioned text (lives, time, portals, accuracy, score, level, cheat/pauses)."""
    draw_text(10, window_height - 30, f"Lives: {player_lives}/{max_lives}")
    elapsed = get_level_elapsed()
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    draw_text(10, window_height - 60, f"Time: {mins:02d}:{secs:02d}")
    draw_text(10, window_height - 90, f"Portals Used: {portals_used}")
    accuracy = (shots_hit / shots_fired * 100) if shots_fired > 0 else 0
    draw_text(10, window_height - 120, f"Accuracy: {accuracy:.1f}%")
    draw_text(10, window_height - 150, f"Score: {game_score}")
    draw_text(10, window_height - 180, f"Level: {current_level}")
    if cheat_mode:
        draw_text(10, window_height - 210, "Cheat: ON")

    if paused:
        draw_text(window_width // 2 - 100, window_height // 2 + 20, "PAUSED")
        draw_text(window_width // 2 - 200, window_height //
                  2 - 10, "Press ESC to resume the game")
        draw_text(window_width // 2 - 200, window_height //
                  2 - 40, "R: Reset | ESC: Resume")
        return

    if not mouse_captured and not game_over and not level_complete:
        draw_text(window_width // 2 - 100,
                  window_height // 2, "Click to Start")
        draw_text(window_width // 2 - 150, window_height //
                  2 - 30, "WASD: Move | Arrow keys: Look")
        draw_text(window_width // 2 - 180, window_height // 2 - 60,
                  "Left Click: Blue Portal | Right Click: Yellow")
        draw_text(window_width // 2 - 100, window_height //
                  2 - 90, "R: Reset | ESC: Menu")


def draw_game_over():
    glColor3f(1.0, 0.0, 0.3)
    draw_text(window_width // 2 - 80, window_height // 2, "GAME OVER")
    glColor3f(1.0, 1.0, 1.0)
    draw_text(window_width // 2 - 100, window_height //
              2 - 40, f"Final Score: {game_score}")
    draw_text(window_width // 2 - 120, window_height //
              2 - 70, "Press R to Restart")


def draw_level_complete():
    glColor3f(0.0, 1.0, 0.5)
    draw_text(window_width // 2 - 100, window_height // 2, "LEVEL COMPLETE!")
    glColor3f(1.0, 1.0, 1.0)
    draw_text(window_width // 2 - 100, window_height //
              2 - 40, f"Score: {game_score}")
    elapsed = get_level_elapsed()
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    draw_text(window_width // 2 - 100, window_height //
              2 - 70, f"Time: {mins:02d}:{secs:02d}")
    if current_level < MAX_LEVEL:
        draw_text(window_width // 2 - 150, window_height //
                  2 - 100, "Press SPACE for Next Level")
    else:
        draw_text(window_width // 2 - 120, window_height //
                  2 - 100, "You Won! Press R to Restart")


def draw_unit_cube():
    """Draw a centered unit cube (-0.5..0.5 on each axis) using GL_QUADS."""
    glBegin(GL_QUADS)
    # +X
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    # -X
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    # +Y
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    # -Y
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    # +Z
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    # -Z
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glEnd()


def draw_gun_fps():
    glPushMatrix()
    glTranslatef(0.2, -0.3, -0.8)

    glPushMatrix()
    glColor3f(0.5, 0.2, 0.8)
    gluCylinder(gluNewQuadric(), 0.07, 0.07, 0.2, 32, 8)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.3, 0.1, 0.5)
    glTranslatef(0.0, 0.0, 0.2)
    gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.6, 32, 8)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.2, 0.1, 0.3)
    glTranslatef(0.0, -0.15, 0.05)
    glRotatef(75, 1, 0, 0)
    glScalef(0.08, 0.3, 0.1)
    draw_unit_cube()
    glPopMatrix()

    glPopMatrix()


class Bullet:
    def __init__(self, pos, direction, color):
        self.pos = list(pos)
        self.velocity = [d * BULLET_SPEED for d in direction]
        self.time_alive = 0.0
        self.color = color


def draw_bullet(bullet):
    glPushMatrix()
    glTranslatef(bullet.pos[0], bullet.pos[1], bullet.pos[2])
    base = PORTAL_BLUE if bullet.color == 'blue' else PORTAL_YELLOW
    glColor3f(*base)
    gluSphere(gluNewQuadric(), BULLET_RADIUS, 16, 16)
    glPopMatrix()


def draw_crosshair():
    """Simple circular crosshair drawn in normalized screen coords (0..1)."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.0, 1.0, 1.0)
    cx, cy = 0.5, 0.5
    r_outer = 0.015
    segments = 64
    pts = []
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        pts.append((cx + math.cos(angle) * r_outer,
                   cy + math.sin(angle) * r_outer))
    glBegin(GL_LINES)
    for i in range(segments):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % segments]
        glVertex3f(x1, y1, 0.0)
        glVertex3f(x2, y2, 0.0)
    glEnd()

    glPointSize(4)
    glBegin(GL_POINTS)
    glVertex3f(cx, cy, 0.0)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# ---------------------------
# Tile & world drawing
# ---------------------------


def draw_tile(tile):
    """Draw a wall tile and, if colored blue/yellow, draw a portal circle on it."""
    coords, color = tile
    # main quad face
    glColor3f(*WALL_COLOR)
    glBegin(GL_QUADS)
    for vertex in coords:
        glVertex3f(vertex[0], vertex[1], vertex[2])
    glEnd()

    # outline
    glColor3f(*WALL_EDGE_COLOR)
    glBegin(GL_LINES)
    for i in range(len(coords)):
        v1 = coords[i]
        v2 = coords[(i + 1) % len(coords)]
        glVertex3f(v1[0], v1[1], v1[2])
        glVertex3f(v2[0], v2[1], v2[2])
    glEnd()

    # draw portal (if present)
    if color in ['blue', 'yellow']:
        x_min, x_max, y_min, y_max, z_min, z_max = min_max_coords(coords)
        z_thin = abs(z_max - z_min) < 0.1
        x_thin = abs(x_max - x_min) < 0.1
        center = [(x_min + x_max) / 2.0, (y_min + y_max) /
                  2.0, (z_min + z_max) / 2.0]
        normal = [0.0, 0.0, 0.0]

        if z_thin:
            normal[2] = 1.0
            radius_x = (x_max - x_min) / 2.0 * 0.92
            radius_y = (y_max - y_min) / 2.0 * 0.92
        elif x_thin:
            normal[0] = 1.0
            radius_x = (z_max - z_min) / 2.0 * 0.92
            radius_y = (y_max - y_min) / 2.0 * 0.92
        else:
            # default fallback (should not happen with wall tiles)
            radius_x = radius_y = 1.0

        portal_color = PORTAL_BLUE if color == 'blue' else PORTAL_YELLOW

        glPushMatrix()
        glTranslatef(center[0] + normal[0] * 0.01, center[1] +
                     normal[1] * 0.01, center[2] + normal[2] * 0.01)
        if normal[0] != 0.0:
            glRotatef(90.0, 0.0, 1.0, 0.0)
        glScalef(radius_x if radius_x > 0.0 else 1.0,
                 radius_y if radius_y > 0.0 else 1.0, 1.0)

        segments = 32
        glColor3f(*portal_color)
        glBegin(GL_QUADS)
        for i in range(segments):
            a1 = 2.0 * math.pi * i / segments
            a2 = 2.0 * math.pi * (i + 1) / segments
            x1, y1 = math.cos(a1), math.sin(a1)
            x2, y2 = math.cos(a2), math.sin(a2)
            glVertex3f(0.0, 0.0, 0.0)
            glVertex3f(x1, y1, 0.0)
            glVertex3f(x2, y2, 0.0)
            glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        glColor3f(*WALL_EDGE_COLOR)
        glBegin(GL_LINES)
        for i in range(segments):
            x1, y1 = math.cos(2.0 * math.pi * i /
                              segments), math.sin(2.0 * math.pi * i / segments)
            x2, y2 = math.cos(2.0 * math.pi * ((i + 1) % segments) /
                              segments), math.sin(2.0 * math.pi * ((i + 1) % segments) / segments)
            glVertex3f(x1, y1, 0.0)
            glVertex3f(x2, y2, 0.0)
        glEnd()
        glPopMatrix()


def draw_floor_and_ceiling():
    """Floor grid and ceiling quad."""
    glColor3f(*FLOOR_COLOR)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(20, 0, 0)
    glVertex3f(20, 0, 20)
    glVertex3f(0, 0, 20)
    glEnd()

    glColor3f(0.7, 0.5, 0.95)
    glBegin(GL_LINES)
    for i in range(21):
        glVertex3f(i, 0.01, 0)
        glVertex3f(i, 0.01, 20)
        glVertex3f(0, 0.01, i)
        glVertex3f(20, 0.01, i)
    glEnd()

    glColor3f(*CEILING_COLOR)
    glBegin(GL_QUADS)
    glVertex3f(0, 9.0, 0)
    glVertex3f(20, 9.0, 0)
    glVertex3f(20, 9.0, 20)
    glVertex3f(0, 9.0, 20)
    glEnd()


def draw_laser_walls():
    """Draw the fixed vertical laser walls and small blocking pieces."""
    for layer in range(3):
        factor = 1.0 - 0.2 * layer
        col = _scale_color(LASER_COLOR, factor)
        glColor3f(*col)
        offset = layer * 0.05
        glBegin(GL_QUADS)
        glVertex3f(0.0, 0.0, 8.5 + offset)
        glVertex3f(4.0, 0.0, 8.5 + offset)
        glVertex3f(4.0, 9.0, 8.5 + offset)
        glVertex3f(0.0, 9.0, 8.5 + offset)

        glVertex3f(5.0, 0.0, 8.5 + offset)
        glVertex3f(9.0, 0.0, 8.5 + offset)
        glVertex3f(9.0, 9.0, 8.5 + offset)
        glVertex3f(5.0, 9.0, 8.5 + offset)

        glVertex3f(4.0, 0.0, 8.5 + offset)
        glVertex3f(5.0, 0.0, 8.5 + offset)
        glVertex3f(5.0, 2.0, 8.5 + offset)
        glVertex3f(4.0, 2.0, 8.5 + offset)

        glVertex3f(4.0, 3.0, 8.5 + offset)
        glVertex3f(5.0, 3.0, 8.5 + offset)
        glVertex3f(5.0, 9.0, 8.5 + offset)
        glVertex3f(4.0, 9.0, 8.5 + offset)
        glEnd()

    for layer in range(3):
        factor = 1.0 - 0.18 * layer
        col = _scale_color(LASER_COLOR, factor)
        glColor3f(*col)
        offset = layer * 0.04
        glBegin(GL_QUADS)
        glVertex3f(9.0 + offset, 0.0, 0.0)
        glVertex3f(9.0 + offset, 0.0, 8.5)
        glVertex3f(9.0 + offset, 9.0, 8.5)
        glVertex3f(9.0 + offset, 9.0, 0.0)
        glEnd()


# ---------------------------
# Horizontal lasers (new)
# ---------------------------


def draw_horizontal_lasers():
    """Draw each horizontal laser as three layered quads for the same look as vertical lasers."""
    for laser in horizontal_lasers:
        z = laser['z']
        y = laser['y']
        half_thick = laser['thickness'] / 2.0
        x_min = laser['x_min']
        x_max = laser['x_max']

        for layer in range(3):
            factor = 1.0 - 0.18 * layer
            col = _scale_color(LASER_COLOR, factor)
            glColor3f(*col)
            y_bottom = y - 0.25 + layer * 0.02
            y_top = y + 0.25 + layer * 0.02
            z0 = z - half_thick + layer * 0.01
            z1 = z + half_thick + layer * 0.01
            glBegin(GL_QUADS)
            glVertex3f(x_min, y_bottom, z0)
            glVertex3f(x_max, y_bottom, z0)
            glVertex3f(x_max, y_top, z1)
            glVertex3f(x_min, y_top, z1)
            glEnd()


def update_horizontal_lasers(dt):
    """Oscillate each laser's y using its amp/freq/phase."""
    if not horizontal_lasers:
        return
    t = now()
    for laser in horizontal_lasers:
        amp = laser.get('amp', 0.25)
        freq = laser.get('freq', 1.0)
        phase = laser.get('phase', 0.0)
        laser['y'] = laser['base_y'] + amp * \
            math.sin(2.0 * math.pi * freq * t + phase)


def generate_horizontal_lasers_for_level(level):
    """
    Generate vertical positions (z tracks) for horizontal lasers.
    """
    horizontal_lasers.clear()
    count = int(level)
    candidates = [5.0, 13.0, 3.0, 15.0, 11.0, 9.0, 7.0, 17.0]

    used = set()
    idx = 0

    while len(horizontal_lasers) < count:
        cand = candidates[idx % len(candidates)]
        idx += 1

        if cand in used:
            continue

        x_min = 0.5
        x_max = room_size - 0.5
        base_y = 0.8
        thickness = 0.4
        amp = 1
        freq = 0.6 + (len(horizontal_lasers) * 0.12)
        phase = (len(horizontal_lasers) * 1.3) % (2 * math.pi)

        horizontal_lasers.append({
            'z': cand,
            'base_y': base_y,
            'y': base_y,
            'thickness': thickness,
            'x_min': x_min,
            'x_max': x_max,
            'amp': amp,
            'freq': freq,
            'phase': phase
        })
        used.add(cand)


# ---------------------------
# Button / moving platform drawing
# ---------------------------


def draw_button(pos=None, activated=False, segments=32):
    if pos is None:
        pos = BUTTON_POS
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glRotatef(-90, 1, 0, 0)
    glColor3f(*DOOR_GREEN if activated else BUTTON_COLOR)
    step = 2 * math.pi / segments
    glBegin(GL_QUADS)
    for i in range(segments):
        angle1 = i * step
        angle2 = (i + 1) * step
        x1 = BUTTON_RADIUS * math.cos(angle1)
        y1 = BUTTON_RADIUS * math.sin(angle1)
        x2 = BUTTON_RADIUS * math.cos(angle2)
        y2 = BUTTON_RADIUS * math.sin(angle2)
        glVertex3f(0, 0, 0)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(0, 0, 0)
    glEnd()
    glPopMatrix()


def draw_moving_platform():
    """Draw all moving obstacles as scaled cubes with a dimmer outer cube."""
    for obs in moving_obstacles:
        x, y, z = obs['pos']
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(*LASER_COLOR)
        glScalef(0.3, 8, 0.3)
        draw_unit_cube()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(x, y, z)
        dim = _scale_color(LASER_COLOR, 0.45)
        glColor3f(*dim)
        glScalef(0.5, 8.5, 0.5)
        draw_unit_cube()
        glPopMatrix()


def draw_door_with_color(tile):
    """If tile is door area (back wall middle), draw it with door_color otherwise draw tile normally."""
    coords, color = tile
    x_min, x_max, y_min, y_max, z_min, z_max = min_max_coords(coords)
    is_door_tile = (abs(z_min - room_size) < 0.1 and y_min <
                    6.0 and 6.67 - 0.1 <= x_min <= 13.33 + 0.1)
    if is_door_tile:
        offset_coords = [[v[0], v[1], v[2] + 0.01] for v in coords]
        glColor3f(*DOOR_GREEN if door_color == 'green' else DOOR_RED)
        glBegin(GL_QUADS)
        for vertex in offset_coords:
            glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

        glColor3f(*WALL_EDGE_COLOR)
        glBegin(GL_LINES)
        for i in range(len(offset_coords)):
            v1 = offset_coords[i]
            v2 = offset_coords[(i + 1) % len(offset_coords)]
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()
    else:
        draw_tile(tile)


# ---------------------------
# Game logic & physics
# ---------------------------


def get_level_elapsed():
    global level_play_accum, level_start_time
    if level_start_time is not None:
        return level_play_accum + (now() - level_start_time)
    return level_play_accum


def ray_plane_intersection(start, end, plane_point, plane_normal):
    direction = [end[i] - start[i] for i in range(3)]
    denom = sum(plane_normal[i] * direction[i] for i in range(3))
    if abs(denom) < 1e-6:
        return None
    t = sum(plane_normal[i] * (plane_point[i] - start[i])
            for i in range(3)) / denom
    if t < 0 or t > 1:
        return None
    return t


def ray_aabb_intersection(start, end, aabb_min, aabb_max):
    """Return True if the segment intersects the AABB or either endpoint is inside."""
    eps = 1e-8
    if _point_in_aabb(start, aabb_min, aabb_max) or _point_in_aabb(end, aabb_min, aabb_max):
        return True
    direction = [end[i] - start[i] for i in range(3)]
    tmin = 0.0
    tmax = 1.0
    for i in range(3):
        if abs(direction[i]) < 1e-9:
            if start[i] < aabb_min[i] - eps or start[i] > aabb_max[i] + eps:
                return False
        else:
            ood = 1.0 / direction[i]
            t1 = (aabb_min[i] - start[i]) * ood
            t2 = (aabb_max[i] - start[i]) * ood
            t_near = min(t1, t2)
            t_far = max(t1, t2)
            tmin = max(tmin, t_near)
            tmax = min(tmax, t_far)
            if tmin > tmax:
                return False
    return (tmin <= tmax and tmin <= 1.0 and tmax >= 0.0)


def update_bullets(dt):
    """Move bullets, check collisions with world and tiles (place portals when hit)."""
    global bullets, wall_tiles, button_activated, shots_hit, game_score, portals_used
    if game_over or level_complete or paused or not mouse_captured:
        return

    new_bullets = []
    collision_margin = max(BULLET_RADIUS * 2.0, 0.25)

    for bullet in bullets:
        bullet.time_alive += dt
        if bullet.time_alive >= BULLET_LIFETIME:
            continue

        old_pos = list(bullet.pos)
        bullet.pos[0] += bullet.velocity[0] * dt
        bullet.pos[1] += bullet.velocity[1] * dt
        bullet.pos[2] += bullet.velocity[2] * dt
        new_pos = bullet.pos

        # kill bullet if out of bounds
        if not (0 <= bullet.pos[0] <= room_size and 0 <= bullet.pos[2] <= room_size and 0 <= bullet.pos[1] <= 9.0):
            continue

        bullet_alive = True

        # keep small laser-wall collision behavior unchanged (plane z ~= 8.5)
        t = ray_plane_intersection(
            old_pos, new_pos, [0.0, 0.0, 8.5], [0.0, 0.0, 1.0])
        if t is not None:
            hit_point = [old_pos[i] + t *
                         (new_pos[i] - old_pos[i]) for i in range(3)]
            if (0.0 <= hit_point[0] <= 9.0 and 0.0 <= hit_point[1] <= 9.0):
                if not (4.0 <= hit_point[0] <= 5.0 and 2.0 <= hit_point[1] <= 3.0):
                    bullet_alive = False
        if not bullet_alive:
            continue

        # x-plane at x=9 wall
        t = ray_plane_intersection(
            old_pos, new_pos, [9.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        if t is not None:
            hit_point = [old_pos[i] + t *
                         (new_pos[i] - old_pos[i]) for i in range(3)]
            if (0.0 <= hit_point[2] <= 8.5 and 0.0 <= hit_point[1] <= 9.0):
                bullet_alive = False
                continue

        # Wall tile collisions -> portal placement
        for ti, tile in enumerate(wall_tiles):
            coords, _ = tile
            x_min, x_max, y_min, y_max, z_min, z_max = min_max_coords(coords)
            aabb_min = [x_min - collision_margin, y_min -
                        collision_margin, z_min - collision_margin]
            aabb_max = [x_max + collision_margin, y_max +
                        collision_margin, z_max + collision_margin]

            if ray_aabb_intersection(old_pos, new_pos, aabb_min, aabb_max):
                _place_portal_on_tile(ti, bullet.color)
                tile[1] = bullet.color
                bullet_alive = False
                shots_hit += 1
                game_score += 10
                break

        if bullet_alive:
            new_bullets.append(bullet)

    bullets = new_bullets


def update_moving_platform(dt):
    """Advance obstacles along their track and reverse direction on bounds."""
    if paused or not mouse_captured or game_over or level_complete:
        return
    for obs in moving_obstacles:
        if obs['direction'] == 'horizontal':
            obs['pos'][0] += obs['speed'] * dt
            if obs['pos'][0] >= obs['max_x'] or obs['pos'][0] <= obs['min_x']:
                obs['speed'] *= -1
        else:
            obs['pos'][2] += obs['speed'] * dt
            if obs['pos'][2] >= obs['max_z'] or obs['pos'][2] <= obs['min_z']:
                obs['speed'] *= -1


def reset_bullets():
    global bullets, portals, tile_portal_map, _next_portal_id
    bullets = []
    portals = []
    tile_portal_map.clear()
    _next_portal_id = 1
    for tile in wall_tiles:
        tile[1] = 'gray'


def update_player_physics(dt):
    """Simple vertical physics (falling) for the player."""
    global player_pos, v_y, is_falling
    if game_over or level_complete or paused or not mouse_captured:
        return
    if is_falling and player_pos[1] > 0.0:
        v_y += GRAVITY * dt
        player_pos[1] += v_y * dt
        if player_pos[1] <= 0.0:
            player_pos[1] = 0.0
            v_y = 0.0
            is_falling = False


def create_wall_with_tiles(start, end, height=9.0, rows=3, cols=12):
    """Create a wall between start and end (x,z pairs) subdivided in rows/cols into tiles."""
    x1, z1 = start
    x2, z2 = end
    dx_total = (x2 - x1)
    dz_total = (z2 - z1)
    dy = height / rows
    for row in range(rows):
        for col in range(cols):
            y_bottom = row * dy
            y_top = (row + 1) * dy
            t_left = col / float(cols)
            t_right = (col + 1) / float(cols)
            x_left = x1 + dx_total * t_left
            z_left = z1 + dz_total * t_left
            x_right = x1 + dx_total * t_right
            z_right = z1 + dz_total * t_right
            tile_coords = [
                (x_left, y_bottom, z_left),
                (x_right, y_bottom, z_right),
                (x_right, y_top, z_right),
                (x_left, y_top, z_left)
            ]
            wall_tiles.append([tile_coords, 'gray'])


def check_player_tile_collision():
    """Teleport player through paired portals when overlapping a portal tile."""
    global player_pos, last_teleport_time, player_yaw, v_y, is_falling, portals_used, game_score
    if game_over or level_complete or paused or not mouse_captured:
        return
    current_time = now()
    if current_time - last_teleport_time < TELEPORT_COOLDOWN:
        return

    for ti, tile in enumerate(wall_tiles):
        coords, color = tile
        if color not in ['blue', 'yellow']:
            continue
        x_min, x_max, y_min, y_max, z_min, z_max = min_max_coords(coords)
        if (x_min - 0.5 <= player_pos[0] <= x_max + 0.5 and
                y_min - 0.5 <= player_pos[1] <= y_max + 0.5 and
                z_min - 0.5 <= player_pos[2] <= z_max + 0.5):

            pid = tile_portal_map.get(ti)
            if pid is None:
                continue
            p = _find_portal_by_id(pid)
            if p is None or p['paired_with'] is None:
                continue
            partner = _find_portal_by_id(p['paired_with'])
            if partner is None:
                continue

            dest_ti = partner['tile_index']
            if 0 <= dest_ti < len(wall_tiles):
                dcoords, _ = wall_tiles[dest_ti]
                dest_x = (min(v[0] for v in dcoords) + max(v[0]
                          for v in dcoords)) / 2
                dest_y = min(v[1] for v in dcoords)
                dest_z = (min(v[2] for v in dcoords) + max(v[2]
                          for v in dcoords)) / 2

                # nudge outwards from wall edges and set yaw to face outward
                if abs(dest_x) < 0.1:
                    dest_x += 2.0
                    player_yaw = 90
                elif abs(dest_x - room_size) < 0.1:
                    dest_x -= 2.0
                    player_yaw = -90
                if abs(dest_z) < 0.1:
                    dest_z += 2.0
                    player_yaw = 180
                elif abs(dest_z - room_size) < 0.1:
                    dest_z -= 2.0
                    player_yaw = 0

                player_pos[0] = dest_x
                player_pos[1] = dest_y
                player_pos[2] = dest_z
                v_y = 0.0
                is_falling = True
                boundary_player_position()
                last_teleport_time = current_time
                portals_used += 1
                game_score += 50
            break


def check_player_laser_collision():
    """Check collisions with small blocking lethal zones, moving obstacles and horizontal lasers."""
    global player_pos, player_lives, game_over
    if game_over or level_complete or paused or not mouse_captured:
        return
    if cheat_mode:
        return

    # small blocking lethal zones unchanged
    if not (0.0 - 0.5 <= player_pos[1] <= 9.0 + 0.5):
        return
    if (0.0 <= player_pos[0] <= 9.0 and 8.0 <= player_pos[2] <= 9.0) or (8.5 <= player_pos[0] <= 9.5 and 0.0 <= player_pos[2] <= 8.5):
        handle_player_death()
        return

    # moving obstacles contact
    for obs in moving_obstacles:
        ox, oy, oz = obs['pos']
        dx = player_pos[0] - ox
        dz = player_pos[2] - oz
        distance = math.sqrt(dx**2 + dz**2)
        if distance < 0.8 and 0 <= player_pos[1] <= 8.5:
            handle_player_death()
            return

    # horizontal lasers contact
    for laser in horizontal_lasers:
        x_min = laser['x_min']
        x_max = laser['x_max']
        z_c = laser['z']
        half_t = laser['thickness'] / 2.0
        y_l = laser['y']

        if x_min - 0.5 <= player_pos[0] <= x_max + 0.5:
            if (z_c - half_t - 0.4) <= player_pos[2] <= (z_c + half_t + 0.4):
                if player_pos[1] <= (y_l + 1.2):
                    handle_player_death()
                    return


def check_door_collision():
    """If player is in back door area and button is activated, complete level."""
    global player_pos, button_activated, level_complete, game_score
    if game_over or level_complete or paused or not mouse_captured:
        return

    in_back = (6.67 - 0.5 <= player_pos[0] <= 13.33 + 0.5 and 0.0 - 0.5 <=
               player_pos[1] <= 6.0 + 0.5 and 19.9 <= player_pos[2] <= 20.1)
    if in_back:
        if button_activated:
            complete_level()


def check_button_interaction():
    """Player stands on button radius and low enough -> activate door and award score."""
    global door_color, button_activated, game_score
    if game_over or level_complete or paused or not mouse_captured:
        return
    if not button_activated:
        dx = player_pos[0] - BUTTON_POS[0]
        dz = player_pos[2] - BUTTON_POS[2]
        distance = math.sqrt(dx * dx + dz * dz)
        if distance <= BUTTON_RADIUS:
            door_color = 'green'
            button_activated = True
            game_score += 100


def handle_player_death():
    """Decrease life or end game and stop timers accordingly."""
    global player_lives, game_over
    player_lives -= 1
    if player_lives <= 0:
        game_over = True
        _stop_level_timer()
    else:
        reset_player_position()


def complete_level():
    """Mark level complete and compute bonuses."""
    global level_complete, game_score
    level_complete = True
    _stop_level_timer()
    elapsed = get_level_elapsed()
    time_bonus = max(0, int(1000 - elapsed * 10))
    game_score += time_bonus
    if shots_fired > 0:
        accuracy = shots_hit / shots_fired
        game_score += int(accuracy * 500)


def reset_player_position():
    """Place player in spawn and reset physics + bullets."""
    global player_pos, player_yaw, player_pitch, v_y, is_falling
    player_pos = [10.0, 0.0, 10.0]
    player_yaw = 0.0
    player_pitch = 0.0
    v_y = 0.0
    is_falling = False
    reset_bullets()


def _start_level_timer():
    global level_start_time, level_play_accum
    if game_over or level_complete:
        return
    if level_start_time is None:
        level_start_time = now()


def _stop_level_timer():
    global level_start_time, level_play_accum
    if level_start_time is not None:
        level_play_accum += (now() - level_start_time)
        level_start_time = None


def reset_game():
    """Reset global state and (re)load level 1."""
    global current_level, player_lives, game_score, shots_fired, shots_hit, portals_used
    global game_over, level_complete, moving_obstacles, paused, level_play_accum, mouse_captured, cheat_mode
    global door_color, button_activated, last_teleport_time, wall_tiles, _next_portal_id

    current_level = 1
    player_lives = max_lives
    game_score = 0
    shots_fired = 0
    shots_hit = 0
    portals_used = 0
    game_over = False
    level_complete = False
    moving_obstacles = []

    reset_player_position()

    door_color = 'red'
    button_activated = False
    last_teleport_time = 0.0

    level_play_accum = 0.0
    level_start_time = None
    paused = False
    mouse_captured = False

    portals[:] = []
    tile_portal_map.clear()
    _next_portal_id = 1

    cheat_mode = False

    load_level(current_level)


# ---------------------------
# Moving obstacle generation
# ---------------------------

def generate_moving_obstacles_for_level(level):
    """
    Create 2 * level moving obstacles.
    Obstacles alternate between horizontal and vertical movement.
    """
    global moving_obstacles
    moving_obstacles.clear()

    total_count = 2 * level
    candidate_positions = [3.0, 4.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0]

    idx = 0
    added = 0

    while added < total_count:
        is_horizontal = (added % 2 == 0)

        if is_horizontal:
            z_choice = candidate_positions[idx % len(candidate_positions)]
            idx += 1

            min_x = 1.0
            max_x = room_size - 1.0
            x = 2.0 + (added * 3) % int(room_size - 4)

            speed = OBSTACLE_SPEED * \
                (1.0 + 0.05 * level) * (1 if added % 4 < 2 else -1)

            moving_obstacles.append({
                'pos': [x, 4.5, z_choice],
                'speed': speed,
                'direction': 'horizontal',
                'min_x': min_x,
                'max_x': max_x,
                'min_z': z_choice,
                'max_z': z_choice
            })
            added += 1

        else:
            x_choice = candidate_positions[idx % len(candidate_positions)]
            idx += 1

            min_z = 1.0
            max_z = room_size - 1.0
            z = 2.0 + (added * 2) % int(room_size - 4)

            speed = OBSTACLE_SPEED * \
                (1.0 + 0.05 * level) * (1 if added % 4 < 2 else -1)

            moving_obstacles.append({
                'pos': [x_choice, 4.5, z],
                'speed': speed,
                'direction': 'vertical',
                'min_x': x_choice,
                'max_x': x_choice,
                'min_z': min_z,
                'max_z': max_z
            })
            added += 1


# ---------------------------
# Level loading & progression
# ---------------------------


def load_level(level):
    """Reset room tiles, obstacles, portals and generate world pieces for the given level."""
    global wall_tiles, button_activated, door_color, level_start_time, moving_obstacles, level_play_accum, paused
    wall_tiles.clear()
    button_activated = False
    door_color = 'red'
    level_play_accum = 0.0
    level_start_time = None
    paused = False
    reset_bullets()
    reset_player_position()
    moving_obstacles = []
    horizontal_lasers.clear()

    # create walls around the room (four edges)
    edges = [((0, 0), (room_size, 0)),
             ((room_size, 0), (room_size, room_size)),
             ((room_size, room_size), (0, room_size)),
             ((0, room_size), (0, 0))]
    for s, e in edges:
        create_wall_with_tiles(s, e)

    # moving obstacles and horizontal lasers
    generate_moving_obstacles_for_level(level)
    generate_horizontal_lasers_for_level(level)


def next_level():
    global current_level, level_complete, mouse_captured
    level_complete = False
    current_level += 1
    if current_level > MAX_LEVEL:
        current_level = MAX_LEVEL
    load_level(current_level)
    mouse_captured = True
    _start_level_timer()


# ---------------------------
# Input handlers
# ---------------------------


def mouse(button, state, x, y):
    global bullets, mouse_captured, shots_fired, level_start_time, level_play_accum, paused
    if paused:
        return
    if game_over or level_complete:
        return

    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            if not mouse_captured:
                mouse_captured = True
                _start_level_timer()
            else:
                if not any_unpaired('blue'):
                    lx = math.sin(math.radians(player_yaw)) * \
                        math.cos(math.radians(player_pitch))
                    ly = math.sin(math.radians(player_pitch))
                    lz = -math.cos(math.radians(player_yaw)) * \
                        math.cos(math.radians(player_pitch))
                    direction = [lx, ly, lz]
                    bullet_pos = [player_pos[0] + lx * 0.8, player_pos[1] +
                                  2.5 + ly * 0.8, player_pos[2] + lz * 0.8]
                    bullets.append(Bullet(bullet_pos, direction, 'blue'))
                    shots_fired += 1

        elif button == GLUT_RIGHT_BUTTON and mouse_captured:
            if not any_unpaired('yellow'):
                lx = math.sin(math.radians(player_yaw)) * \
                    math.cos(math.radians(player_pitch))
                ly = math.sin(math.radians(player_pitch))
                lz = -math.cos(math.radians(player_yaw)) * \
                    math.cos(math.radians(player_pitch))
                direction = [lx, ly, lz]
                bullet_pos = [player_pos[0] + lx * 0.8, player_pos[1] +
                              2.5 + ly * 0.8, player_pos[2] + lz * 0.8]
                bullets.append(Bullet(bullet_pos, direction, 'yellow'))
                shots_fired += 1
    glutPostRedisplay()


def keyboard(key, x, y):
    global player_pos, mouse_captured, level_complete, paused, level_start_time, level_play_accum, cheat_mode, game_over, shots_fired
    key = key.decode("utf-8").lower()

    if key == 'c':
        cheat_mode = not cheat_mode
        return

    if key == '\x1b':
        if not paused:
            paused = True
            _stop_level_timer()
        else:
            paused = False
            if mouse_captured and not game_over and not level_complete:
                _start_level_timer()
        return

    if key == 'r':
        reset_game()
        return

    if key == ' ' and level_complete and current_level < MAX_LEVEL:
        next_level()
        return

    if paused or not mouse_captured or game_over or level_complete:
        return

    if key == 'p':
        reset_bullets()
        return

    lx = math.sin(math.radians(player_yaw))
    lz = -math.cos(math.radians(player_yaw))

    if key == 'w':
        player_pos[0] += lx * cam_speed
        player_pos[2] += lz * cam_speed
    elif key == 's':
        player_pos[0] -= lx * cam_speed
        player_pos[2] -= lz * cam_speed
    elif key == 'a':
        player_pos[0] += lz * cam_speed
        player_pos[2] -= lx * cam_speed
    elif key == 'd':
        player_pos[0] -= lz * cam_speed
        player_pos[2] += lx * cam_speed

    boundary_player_position()
    glutPostRedisplay()


def special_keys(key, x, y):
    global player_yaw, player_pitch
    if paused or game_over or level_complete or not mouse_captured:
        return
    if key == GLUT_KEY_LEFT:
        player_yaw -= yaw_speed
    elif key == GLUT_KEY_RIGHT:
        player_yaw += yaw_speed
    elif key == GLUT_KEY_UP:
        player_pitch += 2
        if player_pitch > 89:
            player_pitch = 89
    elif key == GLUT_KEY_DOWN:
        player_pitch -= 2
        if player_pitch < -89:
            player_pitch = -89
    glutPostRedisplay()


def boundary_player_position():
    min_x, max_x = 0.1, 19.9
    min_z, max_z = 0.1, 19.9
    player_pos[0] = max(min_x, min(max_x, player_pos[0]))
    player_pos[2] = max(min_z, min(max_z, player_pos[2]))


# ---------------------------
# Display, idle, init, main
# ---------------------------


def reshape(w, h):
    global window_width, window_height
    window_width = w
    window_height = h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w / float(h), 0.1, 100)
    glMatrixMode(GL_MODELVIEW)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if game_over:
        _stop_level_timer()
        draw_game_over()
    elif level_complete:
        draw_level_complete()
    else:
        # game state checks each frame
        check_player_tile_collision()
        check_door_collision()
        check_player_laser_collision()
        check_button_interaction()

        lx = math.sin(math.radians(player_yaw)) * \
            math.cos(math.radians(player_pitch))
        ly = math.sin(math.radians(player_pitch))
        lz = -math.cos(math.radians(player_yaw)) * \
            math.cos(math.radians(player_pitch))

        gluLookAt(player_pos[0], player_pos[1] + 2.5, player_pos[2],
                  player_pos[0] + lx, player_pos[1] +
                  2.5 + ly, player_pos[2] + lz,
                  0, 1, 0)

        draw_floor_and_ceiling()
        for tile in wall_tiles:
            draw_door_with_color(tile)

        draw_button(activated=button_activated)
        draw_laser_walls()

        if horizontal_lasers:
            draw_horizontal_lasers()

        if moving_obstacles:
            draw_moving_platform()

        for bullet in bullets:
            draw_bullet(bullet)

        glLoadIdentity()
        draw_gun_fps()
        draw_crosshair()

    draw_hud()
    glutSwapBuffers()


def idle():
    global last_frame_time
    current_time = now()
    dt = current_time - last_frame_time
    last_frame_time = current_time

    if mouse_captured and not paused and not game_over and not level_complete:
        update_bullets(dt)
        update_player_physics(dt)
        update_moving_platform(dt)
        update_horizontal_lasers(dt)
        check_player_tile_collision()
        check_player_laser_collision()

    glutPostRedisplay()


def init():
    global level_start_time, level_play_accum
    glClearColor(*BG_COLOR, 1)
    glutIdleFunc(idle)
    level_start_time = None
    level_play_accum = 0.0
    load_level(1)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Portal Escape")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
