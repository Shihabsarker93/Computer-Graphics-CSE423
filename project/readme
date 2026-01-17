
---

# Portal Escape 🌀🔫

**Portal Escape** is a first-person 3D puzzle-action game built using **Python** and **PyOpenGL (OpenGL + GLUT)**.
Inspired by portal-based mechanics, the player navigates a hazardous room, places paired portals, avoids lasers and moving obstacles, activates buttons, and escapes through a door before running out of lives.

---

## 🎮 Gameplay Overview

* You play in a **single enclosed room** per level.
* Shoot **blue and yellow portals** onto wall tiles.
* Walk through paired portals to teleport across the room.
* Avoid **laser walls**, **horizontal lasers**, and **moving obstacles**.
* Step on a **button** to open the exit door.
* Reach the door to complete the level.
* The game has **5 levels**, each increasing in difficulty.

---

## ✨ Key Features

* First-person camera with mouse-like aiming (keyboard arrows)
* Portal placement and teleportation logic
* Bullet-based portal shooting
* Dynamic obstacles and animated lasers
* Score system with:

  * Time bonus
  * Shooting accuracy bonus
  * Portal usage bonus
* HUD showing lives, time, score, accuracy, and level
* Pause system and cheat mode
* Smooth animations using OpenGL rendering loop

---

## 🛠 Requirements

Make sure you have **Python 3.x** installed, then install the required libraries:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

> ⚠️ On some systems, GLUT comes bundled automatically.
> On Linux, you may need:
>
> ```bash
> sudo apt install freeglut3 freeglut3-dev
> ```

---

## ▶️ How to Run

From the project directory:

```bash
python main.py
```

(Replace `main.py` with the filename that contains the `main()` function if different.)

---

## 🎯 Controls

### Movement

* **W / A / S / D** – Move forward / left / backward / right
* **Arrow Keys** – Look around (yaw & pitch)

### Actions

* **Left Click** – Shoot **Blue Portal**
* **Right Click** – Shoot **Yellow Portal**
* **C** – Toggle Cheat Mode (invincibility)
* **P** – Clear all portals
* **R** – Reset game
* **SPACE** – Next level (after completing a level)
* **ESC**

  * Pause / Resume game
  * Open menu

---

## 🧠 Game Mechanics

### Portals

* Only **one unpaired portal per color** can exist at a time.
* Shooting a wall tile places a portal.
* Walking into a portal teleports you to its paired portal.
* Teleportation has a short cooldown.

### Hazards

* Vertical and horizontal laser walls
* Moving obstacles that patrol paths
* Contact with hazards costs a life (unless cheat mode is active)

### Scoring

* +10 per successful portal hit
* +50 per portal teleport
* +100 for activating the button
* Time and accuracy bonuses on level completion

---

## 🧩 Code Structure (High Level)

* **Rendering**

  * Walls, floors, portals, lasers, bullets, HUD
* **Game Logic**

  * Player movement & physics
  * Collision detection
  * Portal pairing & teleportation
* **Level System**

  * Procedural obstacle & laser generation per level
* **Input Handling**

  * Keyboard, mouse, special keys
* **Main Loop**

  * OpenGL display, idle update, and event callbacks

---

## 🚀 Future Improvements (Ideas)

* Mouse-based camera movement
* Sound effects and background music
* Multiple rooms per level
* Enemies with AI
* Save/load system
* Textures instead of solid colors

---

## 📚 Credits

Developed using:

* **Python**
* **PyOpenGL**
* **GLUT**


