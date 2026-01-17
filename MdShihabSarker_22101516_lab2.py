import random, sys, os, time; from OpenGL.GL import *; from OpenGL.GLUT import *; from OpenGL.GLU import *
class PlayGame:
    def __init__(self):
        self.playEnd, self.paused, self.autoMode, self.count=False, False, False, 0
        self.catcherX, self.catcherY, self.catcherW, self.catcherH, self.catcherSpeed=187, 79, 89, 23, 389.0
        self.Triangle_x = random.randint(17, mac_wid - 17)

        self.Triangle_y = mac_hei - 40
        self.Triangle_speed = 0.25 * mac_hei
        self.speed_step = 39.0
        self.Triangle_color = (1.0, 1.0, 1.0)

        self.options_h = 29
        self.options_w = 29
        self.options_left_x = 39
        self.options_play_x = mac_wid // 2 - self.options_w // 2
        self.options_exit_x = mac_wid - 69

        self.prev_time = time.time()
        self.moving_left ,self.moving_right= False,False

mac_wid = 474
mac_hei = 874
play = PlayGame()
def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2i(int(x), int(y))
    glEnd()
def forward_(point, zone):
    x, y = point
    flip = [(x, y), (y, x), (y, -x), (-x, y),(-x, -y), (-y, -x), (-y, x), (x, -y)]
    return flip[zone]
def backward_(point, zone):
    x, y = point
    flip = [(x, y), (y, x), (-y, x), (-x, y),(-x, -y), (-y, -x), (y, -x), (x, -y)]
    return flip[zone]

def find_zone(dx, dy):
    if abs(dx) < abs(dy): 
        if dx >= 0 and dy >= 0:
            return 1
        elif dx < 0 and dy >= 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else:
            return 6
    elif abs(dx) >= abs(dy): 
        if dx >= 0 and dy >= 0:
            return 0
        elif dx < 0 and dy >= 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        else:
            return 7

def Stright_draw(start, end):
    diffX, diffY = end[0] - start[0], end[1] - start[1]
    zone = find_zone(diffX, diffY)

    p1, p2 = forward_(start, zone), forward_(end, zone)
    diffX, diffY = p2[0] - p1[0], p2[1] - p1[1]

    d = 2 * diffY - diffX
    East = 2 * diffY
    NorthEast = 2 * (diffY - diffX)

    x, y = p1

    while x <= p2[0]:
        prv_x, prv_y = backward_((x, y), zone)
        draw_pixel(prv_x, prv_y)

        if d > 0:
            y = y + 1
            d = d + NorthEast
        else:
            d = d + East

        x = x + 1
def left_buttion():
    glColor3f(0.9, 1.0, 1.0)
    x, y = play.options_left_x, mac_hei - play.options_h
    backCenterX = x + play.options_w // 2
    backCenterY = y + play.options_h // 2
    Stright_draw((backCenterX + 7, backCenterY), (backCenterX - 5, backCenterY))
    Stright_draw((backCenterX - 5, backCenterY), (backCenterX + 2, backCenterY + 7))
    Stright_draw((backCenterX - 5, backCenterY), (backCenterX + 2, backCenterY - 7))

def pause_play():
    glColor3f(0.96, 0.4, 1.0)
    x, y = play.options_play_x, mac_hei - play.options_h
    resumeX = x + play.options_w // 2
    resumeY = y + play.options_h // 2
    if play.paused == False:# ||
        Stright_draw((resumeX - 5, resumeY - 7), (resumeX - 5, resumeY + 7))
        Stright_draw((resumeX + 5, resumeY - 7), (resumeX + 5, resumeY + 7))
    else:
        Stright_draw((resumeX - 6, resumeY - 6), (resumeX - 6, resumeY + 6))
        Stright_draw((resumeX - 6, resumeY + 6), (resumeX + 6, resumeY))
        Stright_draw((resumeX + 6, resumeY), (resumeX - 6, resumeY - 6))


def end_game():
    glColor3f(1.0, 0.5, 0.0)
    crossX, crossY = play.options_exit_x, mac_hei - play.options_h
    Stright_draw((crossX + 5, crossY + 5),(crossX + play.options_w - 5, crossY + play.options_h - 5))
    Stright_draw((crossX + play.options_w - 5, crossY + 5),(crossX + 5,crossY + play.options_h - 5))


def draw_Triangle(x, y): #diamond_
    glColor3f(*play.Triangle_color)
    dimond = [(x, y), (x + 10, y + 15), (x, y + 30), (x - 10, y + 15)] #b, r, t,l
    for i in range(4):
        Stright_draw(dimond[i], dimond[(i + 1) % 4])

def Tray():
    if play.playEnd:
        glColor3f(1.0, 0.0, 0.0)
    else:
        glColor3f(1.0, 1.0, 1.0)

    trayX = play.catcherX
    trayY = play.catcherY
    trayW = play.catcherW
    trayH = play.catcherH

    top_w = trayW
    bottom_w = trayW * 0.7
    offby = (top_w - bottom_w) / 2

    top_left = (trayX, trayY + trayH)
    top_right = (trayX + top_w, trayY + trayH)
    bottom_left = (trayX + offby, trayY)
    bottom_right = (trayX + bottom_w + offby, trayY)
    allpoint = [top_left, top_right, bottom_right, bottom_left]
    for i in range(4):
        Stright_draw(allpoint[i], allpoint[(i + 1) % 4])

def Click_area_inOrOut(x, y, bx, by, bw, bh):
    return bx <= x <= bx + bw and by <= y <= by + bh

def trayAndDiomond_connect(tray_, diamond_):
    return (tray_[0] < diamond_[0] + diamond_[2] and tray_[0] + tray_[2] > diamond_[0] and tray_[1] < diamond_[1] + diamond_[3] and tray_[1] + tray_[3] > diamond_[1])

def make_color():
    r = random.uniform(0.4, 1.0)
    g = random.uniform(0.4, 1.0)
    b = random.uniform(0.4, 1.0)
    return (r, g, b)

def spawn_new_Triangle():
    play.Triangle_y = 838
    play.Triangle_x = random.randint(17, mac_wid - 17)
    play.Triangle_color = make_color()


def reset_game():
    print("Score is rest")
    play.count = 0
    play.Triangle_speed = 123.0
    spawn_new_Triangle()
    play.catcherX = (mac_wid ) // 2
    play.playEnd = False
    play.paused = False
    play.autoMode = False

def Click_input(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = mac_hei - y
        if Click_area_inOrOut(x, y, play.options_exit_x, mac_hei - play.options_h, play.options_w, play.options_h):
            print(f"Your Final Score: {play.count}")
            try:
                glutLeaveMainLoop()
            except Exception:
                os._exit(0)
        elif Click_area_inOrOut(x, y, play.options_play_x, mac_hei - play.options_h, play.options_w, play.options_h):
            play.paused = not play.paused
        elif Click_area_inOrOut(x, y, play.options_left_x, mac_hei - play.options_h, play.options_w, play.options_h):
            reset_game()



def special_paused(key, x, y): #key paused
    if play.playEnd or play.paused:
        return
    if key == GLUT_KEY_LEFT:
        play.moving_left = True
    elif key == GLUT_KEY_RIGHT:
        play.moving_right = True
    glutPostRedisplay()
def special_release(key, x, y): #
    if key == GLUT_KEY_LEFT:
        play.moving_left = False
    elif key == GLUT_KEY_RIGHT:
        play.moving_right = False

def on_keyboard(key, x, y):
    if key in (b'c'):
        play.autoMode = not play.autoMode
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    if not play.playEnd or play.paused:
        draw_Triangle(play.Triangle_x, play.Triangle_y)
    Tray()
    left_buttion()
    pause_play()
    end_game()
    glutSwapBuffers()

def update_game():
    cur_time = time.time()
    calc_deltaTime = max(0.0, min(0.05, cur_time - play.prev_time))
    play.prev_time = cur_time

    if not play.playEnd and not play.paused:

        if play.moving_left:
            play.catcherX = max(0, play.catcherX - play.catcherSpeed * calc_deltaTime) 
        if play.moving_right:
            play.catcherX = min(mac_wid - play.catcherW, play.catcherX + play.catcherSpeed * calc_deltaTime) 
        
        play.Triangle_y -= play.Triangle_speed * calc_deltaTime

        if play.Triangle_y <= play.catcherY + play.catcherH:
            catcher_invisible = (play.catcherX, play.catcherY, play.catcherW, play.catcherH) 
            dimond_invible_box = (play.Triangle_x - 10, play.Triangle_y, 20, 30) 
            if trayAndDiomond_connect(catcher_invisible, dimond_invible_box):
                play.count += 1
                print(f"Score: {play.count}")
                play.Triangle_speed = min(play.Triangle_speed + play.speed_step, 700)
                play.catcherSpeed = min(389.0 + play.count * 8, 750) 
                spawn_new_Triangle()
            elif play.Triangle_y <= 0: 
                play.playEnd = True
                print(f"You lost man, :( Score: {play.count}")

        if play.autoMode:
            target_x = max(0, min(mac_wid - play.catcherW, play.Triangle_x - play.catcherW // 2)) #
            diff = target_x - play.catcherX 
            if abs(diff) > 2:
                move_speed = abs(diff) * 7.8
                if move_speed > 1190:
                    move_speed = 1190
                if diff > 0:
                    play.catcherX += move_speed * calc_deltaTime
                else:
                    play.catcherX -= move_speed * calc_deltaTime
                if abs(target_x - play.catcherX) < 2: #spawn
                    play.catcherX = target_x
    glutPostRedisplay()

def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    gluOrtho2D(0, mac_wid, 0, mac_hei)
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(mac_wid, mac_hei)
    glutCreateWindow(b"Iphone 20 Pro max view")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(update_game)
    glutSpecialFunc(special_paused)
    glutSpecialUpFunc(special_release)
    glutKeyboardFunc(on_keyboard)
    glutMouseFunc(Click_input)
    glutMainLoop()
if __name__ == "__main__":
    main()