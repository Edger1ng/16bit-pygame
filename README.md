# 16bit-pygame

An **simple game** made on **Python** + **Pygame**

## Features

- GUI-map editor
- **simple** AI **simulating** for Enemy
- Automatic map **generation**
- Console in-game (**Ctrl+E**)
- **Super-additions** for player
- Player **control**

## Screenshot

![Screenshot][readme/main.png]

## Install

You can install it all for yourself if you want to.Altrough, you can grab **ready-made Github Actions file**

```
git clone https://github.com/Edger1ng/16bit-pygame.git
cd 16bit-pygame
pip install pygame
pytho main.py
```

**or**

```
https://github.com/Edger1ng/16bit-pygame/actions
```

## Details about game

### Player

- You can control player **using WASD buttons**
- You can use one of supercharges **every 10 seconds**
- Your point is to **go to the finish**
- Don't fall into **red points** , they give you **-40% of health**

### Enemy

- Enemy's point is to **catch player**
- He destroy 3x3 walls **every 15 seconds**
- He has **30% speed up when he see's player**
- He use **simulation of AI** to have orientation in the game

## Structure of project

my_game/
├── astar.py         
├── enemy.py         
├── gui.py           
├── main.py          
├── player.py        
├── settings.py      
├── tilemap.py       
└── README.md        
