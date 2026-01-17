from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

cPos, cAngle, cHei, cRedius = [0, -600, 600], 0, 500, 500
fldOfView, gridLen, rand_var = 120, 600, 333
personPos, personAngle, personLife, total_score, negative_score, gOverFlag = [0, 0, 50], 30, 5, 0, 0, False
cheatMode, cheatView, fppView = False, False, False
time_count, oponent, balls = 0, [], []

ballSpeed = 9
oppSpeed = 0.6
oppNumAtTime = 5
rotation_speed = 2.1


prevLife = personLife
prevScore = total_score
prevNegScore = negative_score

def keyboardListener(key, x, y):
    global personPos, personAngle, cheatMode, cheatView, fppView

    if key == b'r':
        initialize_game()
        return
    if gOverFlag is True:
        return
    # f/b movement
    if key == b'w' or key == b's':
        if key == b'w':
            moveAngle = personAngle + 90 # y +ve
        else:
            moveAngle = personAngle + 270 #y -ve

        radianValue = math.radians(moveAngle)
        proposedX = personPos[0] + 40 * math.cos(radianValue)
        proposedY = personPos[1] + 40 * math.sin(radianValue)
        personPos[0] = max(-gridLen + 50, min(gridLen - 50, proposedX))# bounary
        personPos[1] = max(-gridLen + 50, min(gridLen - 50, proposedY))

    
    elif key == b'a':
        personAngle = (personAngle + 5) % 360 #  
    
    elif key == b'd':
        personAngle = (personAngle - 5) % 360
    
    elif key == b'c' or key == b'C': #cheat togle
        if cheatMode:
            cheatMode = False
            cheatView = False
            fppView = False
        else:
            cheatMode = True
    elif key == b'v': #cv t
        if cheatMode is False:
            return
        cheatView = not cheatView
        fppView = cheatView
    #
    elif key == b'f': #fp t
        fppView = not fppView


def specialKeyListener(key, x, y):
    global cAngle, cHei

    if gOverFlag is True:
        return
    if key == GLUT_KEY_LEFT or key == GLUT_KEY_RIGHT: #cam hori
        if key == GLUT_KEY_LEFT:
            cAngle = cAngle - 5
        else:
            cAngle = cAngle + 5
    elif key == GLUT_KEY_UP or key == GLUT_KEY_DOWN: #cam Hehi
        if key == GLUT_KEY_UP:
            if cHei >= 800:
                return
            cHei = cHei + 10
        else:
            if cHei <= 100:
                return
            cHei = cHei - 10


def mouseListener(button, state, x, y):
    global fppView

    if gOverFlag is True:
        return
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN: #fpp tgl
        fppView = not fppView
        return

    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN: #fire bu
        return

    fireAngle = math.radians(personAngle + 90)
    spawnDistance = 87
    heightOffset = 20

    if fppView is True: #adjsut tpp
        spawnDistance = 140
        heightOffset = -20

    bulletX = personPos[0] + spawnDistance * math.cos(fireAngle)
    bulletY = personPos[1] + spawnDistance * math.sin(fireAngle)
    bulletZ = personPos[2] + heightOffset #z offset/ hei

    balls.append([
        bulletX,
        bulletY,
        bulletZ,
        (personAngle + 90) % 360
    ])


def draw_player():
    glPushMatrix()
    glTranslatef(personPos[0], personPos[1], personPos[2])

    if gOverFlag == True:
        glRotatef(90, 1, 0, 0) #x axis inverse

    glRotatef(personAngle, 0, 0, 1) #z axis rot

    if fppView == True: #fpp model
        glTranslatef(0, 50, -70) #ektu age

        glPushMatrix() #right arm
        glColor3f(200 / 255, 157 / 255, 124 / 255)
        glTranslatef(30, 15, 30)
        glRotatef(-45, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 6, 50, 10, 10)
        glPopMatrix()

        glPushMatrix() #left a
        glColor3f(200 / 255, 157 / 255, 124 / 255)
        glTranslatef(-30, 15, 30)
        glRotatef(-50, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 6, 50, 10, 10)
        glPopMatrix()

        glPushMatrix() #fpp gun
        glColor3f(192 / 255, 192 / 255, 192 / 255)
        glTranslatef(0, 15, 30)
        glRotatef(-45, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 15, 5, 60, 10, 10)
        glPopMatrix()

    else:
        glPushMatrix() #left leg
        glColor3f(0.2, 0.2, 0.8) #tpp model
        glTranslatef(-18, 0, -30)
        gluCylinder(gluNewQuadric(), 8, 14, 55, 12, 12)
        glPopMatrix()

        glPushMatrix() #rig l
        glColor3f(0.2, 0.2, 0.8)
        glTranslatef(18, 0, -30)
        gluCylinder(gluNewQuadric(), 8, 14, 55, 12, 12)
        glPopMatrix()

        glPushMatrix() #body
        glTranslatef(0, 0, 50)

        glPushMatrix() #
        glColor3f(0.45, 0.30, 0.15)
        glutSolidCube(60)
        glPopMatrix()

        glPushMatrix() #righ arm
        glColor3f(0.85, 0.72, 0.62)
        glTranslatef(35, 7, 15)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 6, 60, 12, 12)
        glPopMatrix()

        glPushMatrix() #left a
        glColor3f(0.85, 0.72, 0.62)
        glTranslatef(-35, 7, 15)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 6, 60, 12, 12)
        glPopMatrix()

        glPushMatrix() #gun
        glColor3f(0.6, 0.6, 0.6)
        glTranslatef(0, 27, 20)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 12, 5, 65, 12, 12)
        glPopMatrix()

        glPushMatrix() #head
        glColor3f(0.1, 0.1, 0.1)
        glTranslatef(0, 0, 50)
        gluSphere(gluNewQuadric(), 25, 20, 20)
        glPopMatrix()

        glPopMatrix()

    glPopMatrix()


def drawthread(x, y, z, scale):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 0, 0)
    coreRadius = 27 * scale
    gluSphere(gluNewQuadric(), coreRadius, 20, 20)
    glTranslatef(0, 0, coreRadius + 9.55 * scale)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 12 * scale, 20, 20)
    glPopMatrix()


def drawBalls(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.88, 0.4, 0)
    glutSolidCube(9.8)
    glPopMatrix()


def draw_shapes():
    makeGrindAndTile()
    draw_player()
    for enemy in oponent:
        drawthread(*enemy[:3], enemy[3])
    for fire in balls:
        drawBalls(*fire[:3])


def threadSpawn():
    edgeIndex = random.randint(0, 3)

    if edgeIndex >= 2: #left/right
        y = random.uniform(-gridLen + 60, gridLen - 60)
        if edgeIndex == 2:
            x = -gridLen + 60
        else:
            x = gridLen - 60
    else: #top/bottom
        x = random.uniform(-gridLen + 60, gridLen - 60)
        if edgeIndex == 0:
            y = gridLen - 60
        else:
            y = -gridLen + 60

    return [x, y, 30, 1.0]


def initialize_game():
    global personPos, personAngle, personLife, total_score, negative_score
    global gOverFlag, cheatMode, cheatView, fppView
    global oponent, balls, time_count
    global prevLife, prevScore, prevNegScore
    global cAngle, cHei
    #all reset
    personPos, personAngle, personLife, total_score, negative_score, gOverFlag = [0, 0, 30], 0, 5, 0, 0, False #reset
    cheatMode, cheatView, fppView = False, False, False
    time_count, cAngle, cHei = 0, 0, 500

    oponent = []
    index = 0
    while index < oppNumAtTime:
        oponent.append(threadSpawn())
        index = index + 1

    balls = []

    prevLife = personLife
    prevScore = total_score
    prevNegScore = negative_score


def gameStateUpdate():
    global time_count, oponent, balls, personLife, negative_score
    global total_score, gOverFlag, personAngle
    global prevLife, prevScore, prevNegScore

    if gOverFlag:
        return

    time_count = time_count + 0.02 #inc animaiton time
    updatedEnemies = []
    lostLife = False

    for ex, ey, ez, _ in oponent: #eney and collution
        pulseScale = 0.8 + 0.4 * math.sin(time_count * 2)
        vx = personPos[0] - ex
        vy = personPos[1] - ey #cal vector to player
        distance = math.hypot(vx, vy)

        if distance != 0: #move to player
            ex = ex + (vx / distance) * oppSpeed
            ey = ey + (vy / distance) * oppSpeed

        hitRadius = 30 * pulseScale #collution check

        if distance < hitRadius + 30: #collutio
            if lostLife is False:
                personLife = personLife - 1
                lostLife = True
            updatedEnemies.append(threadSpawn())
        else:
            updatedEnemies.append([ex, ey, ez, pulseScale])

    oponent = updatedEnemies
    updatedBalls = []
    # bullet update and collution
    for bx, by, bz, ang in balls: #bullet update
        moveRad = math.radians(ang)
        bx = bx + ballSpeed * math.cos(moveRad)
        by = by + ballSpeed * math.sin(moveRad)

        if abs(bx) > gridLen or abs(by) > gridLen: #check bulelt out of bound s
            negative_score = negative_score + 1
            continue

        struck = False
        for idx in range(len(oponent)):
            ex, ey, _, sc = oponent[idx]
            if math.hypot(bx - ex, by - ey) < (30 * sc) + 5:
                total_score = total_score + 1
                oponent[idx] = threadSpawn()
                struck = True
                break

        if struck is False:
            updatedBalls.append([bx, by, bz, ang])

    balls = updatedBalls

    if cheatMode: #auto aim
        personAngle = (personAngle + rotation_speed) % 360 #auto rotate
        for ex, ey, _, _ in oponent:
            dx = ex - personPos[0]
            dy = ey - personPos[1]
            targetAngle = math.degrees(math.atan2(dy, dx)) % 360
            gunDir = (personAngle + 90) % 360
            diff = abs((targetAngle - gunDir + 180) % 360 - 180)
            if diff < 1:
                balls.append([personPos[0], personPos[1], personPos[2] + 20, gunDir])
                break

    if prevLife != personLife:
        print("Lives left:", personLife)
        prevLife = personLife

    if prevScore != total_score:
        print("Score updated:", total_score)
        prevScore = total_score

    if prevNegScore != negative_score:
        print("Miss counter:", negative_score)
        prevNegScore = negative_score


    if personLife <= 0 or negative_score >= 10: #game over?
        if gOverFlag is False:
            print("Session ended")
            print("Score:", total_score)
            print("Lives:", personLife)
            print("Misses:", negative_score)
        gOverFlag = True


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if fppView:
        gluPerspective(90, 1.25, 1.0, 1500) #fpp fov
    else:
        gluPerspective(fldOfView, 1.25, 1.0, 1500) #tpp fov FOV, aspect ratio, near, far

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

   
    if fppView is True: #if fpp ture fllow player
        radianAngle = math.radians(personAngle + 90)
        camX = personPos[0]
        camY = personPos[1]
        camZ = personPos[2] + 60
        lookDistance = 120

        if cheatMode and cheatView:
            lookDistance = 200

        targetX = camX + lookDistance * math.cos(radianAngle)
        targetY = camY + lookDistance * math.sin(radianAngle)
        targetZ = camZ - 20

        gluLookAt(camX, camY, camZ, targetX, targetY, targetZ, 0, 0, 1)
        return
    #else dont follow rotate
    orbitRad = math.radians(cAngle) #tpp
    cPos[0] = cRedius * math.cos(orbitRad)
    cPos[1] = cRedius * math.sin(orbitRad)
    cPos[2] = cHei

    gluLookAt(cPos[0], cPos[1], cPos[2], 0, 0, 60, 0, 0, 1)


def idle():
    gameStateUpdate()
    glutPostRedisplay()


def showScreen():
    glViewport(0, 0, 1000, 800) #f
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    setupCamera()
    draw_shapes()

    #hdd text
    glColor3f(1, 1, 0)
    applyletters(10, 770, "Points: " + str(total_score))

    glColor3f(0.3, 1, 0.3)
    applyletters(10, 740, "Health: " + str(personLife))

    glColor3f(1, 0.5, 0.5)
    applyletters(10, 710, "Missed Shots: " + str(negative_score))

    if cheatMode:
        glColor3f(0.5, 0.8, 1)
        applyletters(10, 680, "Assist ON")

        if cheatView:
            glColor3f(0.8, 0.5, 1)
            applyletters(10, 650, "Vision ON")

    if gOverFlag:
        glColor3f(1, 0, 0)
        applyletters(360, 400, "Mission Failed")
        glColor3f(1, 1, 1)
        applyletters(360, 370, "Final Points: " + str(total_score))
        applyletters(360, 340, "Press R to Retry")

    glutSwapBuffers()


def applyletters(x, y, letters, textLook=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in letters:
        glutBitmapCharacter(textLook, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def makeGrindAndTile():
    cellSize = 60
    cellCount = gridLen // cellSize
    limit = cellCount * cellSize

    glBegin(GL_QUADS)

    for gx in range(-cellCount, cellCount):
        for gy in range(-cellCount, cellCount):
            left = gx * cellSize
            right = (gx + 1) * cellSize
            bottom = gy * cellSize
            top = (gy + 1) * cellSize

            if (gx + gy) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.7, 0.5, 0.95)

            glVertex3f(left, bottom, 0)
            glVertex3f(right, bottom, 0)
            glVertex3f(right, top, 0)
            glVertex3f(left, top, 0)

    glEnd()

    wallHeight = 185
    glBegin(GL_QUADS)

    glColor3f(0.1, 0.8, 1)
    glVertex3f(-limit, limit, 0)
    glVertex3f(limit, limit, 0)
    glVertex3f(limit, limit, wallHeight)
    glVertex3f(-limit, limit, wallHeight)

    glColor3f(0.2, 0.8, 0.2)
    glVertex3f(-limit, -limit, 0)
    glVertex3f(limit, -limit, 0)
    glVertex3f(limit, -limit, wallHeight)
    glVertex3f(-limit, -limit, wallHeight)

    glColor3f(0.67, 0.11, 1)
    glVertex3f(-limit, -limit, 0)
    glVertex3f(-limit, limit, 0)
    glVertex3f(-limit, limit, wallHeight)
    glVertex3f(-limit, -limit, wallHeight)

    glColor3f(0.55, 1, 0)
    glVertex3f(limit, -limit, 0)
    glVertex3f(limit, limit, 0)
    glVertex3f(limit, limit, wallHeight)
    glVertex3f(limit, -limit, wallHeight)

    glEnd()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"fire Frenzy")

    initialize_game()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
