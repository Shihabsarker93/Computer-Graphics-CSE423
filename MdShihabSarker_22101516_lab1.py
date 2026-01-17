

#task1

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

tank, water, waterAngle, max_angle = 800, [], 0, 20.0
sR, sG, sB = 0.1, 0.1, 0.2
dayNight = False
pre_time = time.time()

def type_value(key, x, y):
    global dayNight
    if key == b'x' :
        dayNight = True
    else:
        dayNight = False

def special_key_listener(key, x, y):
    global waterAngle, max_angle
    if key == GLUT_KEY_RIGHT and waterAngle < max_angle:
            waterAngle = waterAngle + 1.5
    if key == GLUT_KEY_LEFT and waterAngle > -max_angle:
            waterAngle = waterAngle - 1.5

def sky():
    global sR, sG, sB

    glBegin(GL_TRIANGLES)
    glColor3f(sR, sG, sB)

    # Tr1
    glVertex2f(-1.0, 1)
    glVertex2f(1.0, 1)
    glVertex2f(-1.0, 0.6)

    # Tri2
    glVertex2f(1.0, 1)
    glVertex2f(-1.0, 0.6)
    glVertex2f(1.0, 0.6)
    glEnd()

def mud():
    glBegin(GL_TRIANGLES)
    # Muddy brown color
    glColor3f(0.36, 0.25, 0.20)

    glVertex2f(-1, 0.6)
    glVertex2f(1, 0.6)
    glVertex2f(-1, -1)

    glVertex2f(1, 0.6)
    glVertex2f(-1, -1)
    glVertex2f(1, -1)
    glEnd()


def init_rain():
    global water
    water = []

    for w in range(tank):
        x = random.uniform(-1.0, 1.0)
        y = random.uniform(-1.0, 1.0)
        speed = random.uniform(0.005, 0.009)
        water.append([x, y, speed])
def strom():
    global water, waterAngle
    glLineWidth(2)
    glColor3f(0.26, 0.59, 1)
    glBegin(GL_LINES)

    for w in range(tank):
        x = water[w][0]
        y = water[w][1]
        upDown =  0.04
        radians = math.radians(waterAngle)
        rightLeft = radians * upDown
        glVertex2f(x, y)
        glVertex2f(x + rightLeft, y - upDown)

    glEnd()

def update_rain():
    global water, waterAngle
    radians = math.radians(waterAngle)        
    x_shift = radians * 0.0015       

    for i in range(tank):
        speed = water[i][2]
        water[i][1] -= speed                    
        water[i][0] += x_shift             
        if  water[i][0] < -17 or water[i][0] > 17 or water[i][1] < -1.0 :
            water[i][0] = random.uniform(-2.0, 2.0)
            water[i][1] = 1.0
            water[i][2] = random.uniform(0.004, 0.018)


def hills():
    height_Tree = 0.25 # Tree peaks (made smaller)
    noTree = 20
    i = 0
    gap = 2 / float(noTree) # -1 to 1
    for i in range(noTree):
        leftPoint = -1.0 + i * gap
        rightPoint = leftPoint + gap
        midVal = (leftPoint + rightPoint) / 2
        glBegin(GL_TRIANGLES)
        glColor3f(0, 0.8, 0)
        glVertex2f(leftPoint, 0)
        glVertex2f(rightPoint, 0)
        glColor3f(0.3, 1, 0.3)
        glVertex2f(midVal, height_Tree)
        glEnd()



def home():
    Min_ = -0.4
    max_ = 0.29
    hosueXval = 0.35
    glColor3f(1, 0.7, 0.5)
    glBegin(GL_TRIANGLES)  # house body
    glVertex2f(-hosueXval, Min_)
    glVertex2f(hosueXval, Min_)
    glVertex2f(-hosueXval, max_)  # second tri
    glVertex2f(hosueXval, max_)
    glVertex2f(-hosueXval, max_)
    glVertex2f(hosueXval, Min_)
    glEnd()

    # Roof (triangle)
    glColor3f(0.45, 0.18, 0.75)
    glBegin(GL_TRIANGLES)
    glVertex2f(-hosueXval - 0.05, 0.29)
    glVertex2f(0, max_ + 0.25)
    glVertex2f(hosueXval + 0.05, 0.29)
    glEnd()

    dL = -0.07
    dR = 0.07

    glColor3f(1, 0, 1)  # door
    glBegin(GL_TRIANGLES)
    glVertex2f(dL, Min_)
    glVertex2f(dR, Min_)
    glVertex2f(dL, 0)

    glVertex2f(dR, 0)
    glVertex2f(dL, 0)
    glVertex2f(dR, Min_)
    glEnd()

    glColor3f(0, 1, 0)  # knob
    glPointSize(5)
    glBegin(GL_POINTS)
    glVertex2f(0.04, Min_ + 0.17)
    glEnd()

    # Right window (bigger, same center)
    wintwo_l = 0.10
    wintwo_r = 0.27
    wintwo_b = Min_ + 0.23
    wintwo_t = Min_ + 0.40

    glColor3f(0.38, 1, 1)
    glBegin(GL_TRIANGLES)
    glVertex2f(wintwo_r, wintwo_t)
    glVertex2f(wintwo_l, wintwo_t)
    glVertex2f(wintwo_r, wintwo_b)
    glVertex2f(wintwo_l, wintwo_b)
    glVertex2f(wintwo_r, wintwo_b)
    glVertex2f(wintwo_l, wintwo_t)
    glEnd()

    # Right window panes
    glColor3f(0, 0, 0)
    glLineWidth(2)
    glBegin(GL_LINES)
    HrizntalMid = (wintwo_b + wintwo_t) / 2.0
    glVertex2f(wintwo_l, HrizntalMid)
    glVertex2f(wintwo_r, HrizntalMid)
    VarticalMid = (wintwo_l + wintwo_r) / 2.0
    glVertex2f(VarticalMid, wintwo_b)
    glVertex2f(VarticalMid, wintwo_t)
    glEnd()

    # Left window (bigger, same center)
    winOne_l = -0.27
    winOne_r = -0.10
    winOne_b = Min_ + 0.23
    winOne_t = Min_ + 0.40

    glColor3f(0.38, 1, 1)
    glBegin(GL_TRIANGLES)
    glVertex2f(winOne_l, winOne_b)
    glVertex2f(winOne_r, winOne_b)
    glVertex2f(winOne_l, winOne_t)

    glVertex2f(winOne_r, winOne_t)
    glVertex2f(winOne_l, winOne_t)
    glVertex2f(winOne_r, winOne_b)
    glEnd()

    # Left window panes
    glColor3f(0, 0, 0)
    glLineWidth(2)
    glBegin(GL_LINES)
    HrizntalMid = (winOne_b + winOne_t) / 2.0
    glVertex2f(winOne_l, HrizntalMid)
    glVertex2f(winOne_r, HrizntalMid)
    VarticalMid = (winOne_l + winOne_r) / 2.0
    glVertex2f(VarticalMid, winOne_b)
    glVertex2f(VarticalMid, winOne_t)
    glEnd()



def animate():
    update_rain()
    daytonight_(dayNight)
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    sky()
    mud()
    hills()
    home()
    strom()
    glutSwapBuffers()

def daytonight_(new_update):
    global sR, sG, sB, pre_time
    curVal = time.time()
    working_val = curVal - pre_time
    pre_time = curVal
    morR, morG, morB = 0.53, 0.81, 0.92
    nR, nG, nB = 0.05, 0.05, 0.15
    speed = 0.7 * working_val
    if new_update:
        sR += (morR - sR) * speed
        sG += (morG - sG) * speed
        sB += (morB - sB) * speed
    else:
        sR += (nR - sR) * speed
        sG += (nG - sG) * speed
        sB += (nB - sB) * speed


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(1440, 840)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Task1")
    init_rain()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(type_value)
    glutSpecialFunc(special_key_listener)
    glutMainLoop()

if __name__ == "__main__":
    main()












#task2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

W_W, W_H = 600, 600
X, Y, VX, VY, C0, C = [], [], [], [], [], []
spd = 0.015
rds = 12
blink = False
hold = False
bt = 0.0

def conv(px, py):
    gy = (W_H / 2) - py
    gx = px - (W_W / 2)
    return gx, gy

def draw_dot(xp, yp, sz, col):
    glBegin(GL_POINTS)
    glColor3f(col[0], col[1], col[2])
    glVertex2f(xp, yp)
    glEnd()
    glPointSize(sz)

def values_key(k, a, b):
    global hold
    if k == b' ':
        hold = not hold
    glutPostRedisplay()

def speacial_key(k, a, b):
    global spd
    if k == GLUT_KEY_DOWN:
        spd = max(0.005, spd / 1.5)
    elif k == GLUT_KEY_UP:
        spd *= 1.5
    glutPostRedisplay()

def touchPad(btn, state, mx, my):
    global blink
    if btn == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        blink = not blink
    elif btn == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        gx, gy = conv(mx, my)
        dx, dy = random.choice([(1,1), (-1,1), (1,-1), (-1,-1)])
        c1 = random.uniform(0.3, 1.0)
        c2 = random.uniform(0.3, 1.0)
        c3 = random.uniform(0.3, 1.0)
        col = [c1, c2, c3]
        X.append(gx)
        Y.append(gy)
        VX.append(dx)
        VY.append(dy)
        C0.append(col)
        C.append(col[:])
    glutPostRedisplay()

def viewPoint():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    for i in range(len(X)):
        draw_dot(X[i], Y[i], rds, C[i])
    glutSwapBuffers()

def allMove():
    global bt
    if hold == False:
        n = len(X)
        for i in range(n):
            X[i] += spd * VX[i]
            Y[i] += spd * VY[i]
            if X[i] >= 280 or X[i] <= -280:
                VX[i] = -VX[i]
            if Y[i] >= 280 or Y[i] <= -280:
                VY[i] = -VY[i]

        if blink:
            bt = bt + 0.12
            f = abs((bt % 2) - 1)
            for i in range(n):
                R, G, B = C0[i]
                C[i] = [R*f, G*f, B*f]
        else:
            for i in range(n):
                C[i] = C0[i][:]
    glutPostRedisplay()

def final_():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-300, 300, -300, 300, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glClearColor(0.05, 0.05, 0.1, 0)

glutInit()
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowPosition(80, 80)
glutInitWindowSize(W_W, W_H)
glutCreateWindow(b"Task 2 - Dot Animation")
final_()
glutKeyboardFunc(values_key)
glutSpecialFunc(speacial_key)
glutMouseFunc(touchPad)
glutDisplayFunc(viewPoint)
glutIdleFunc(allMove)
glutMainLoop()
