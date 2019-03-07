from typing import Tuple

import psutil
import os

import math

import pythoncom
import pyWinhook as pyHook

import ctypes


MOVING: int = 512
DOWN: int = 513
UP: int = 514

MIN_DELAY: int = 250  # ms
MIN_DISTANCE: int = 10

mouseLock: bool = False
mouseIsUp: bool = True
lastClickUpTime: int = 0
lastClickUpPos: Tuple[int, int] = (-1, -1)
lastClickRealDownPos: Tuple[int, int] = (-1, -1)


def messages(event):
    print('MessageName:', event.MessageName)
    print('Message:', event.Message)
    print('Time:', event.Time)
    print('Window:', event.Window)
    print('WindowName:', event.WindowName)
    print('Position:', event.Position)
    print('Wheel:', event.Wheel)
    print('Injected:', event.Injected)
    print('---')


def set_high_priority():
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)


def get_distance(pos_1, pos_2):
    return math.sqrt((pos_2[0] - pos_1[0])**2 + (pos_2[1] - pos_1[1])**2)


def mouse_up(hndl, pos):
    print('mouse_up')
    hndl.UnhookMouse()
    import win32con
    ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTUP, pos[0], pos[1], 0, 0)
    hndl.HookMouse()


def on_mouse_event(event):
    global hm

    global MOVING
    global DOWN
    global UP

    global MIN_DELAY

    global mouseLock
    global mouseIsUp
    global lastClickUpTime
    global lastClickUpPos
    global lastClickRealDownPos

    # called when mouse events are received
    # messages(event)

    # print(event.Time, mouseState, mouseIsSelecting, mouseStateInSelection,
    # get_distance(lastClickDownPos, event.Position), event.Message)

    # TO DO: if moved less than MIN_DISTANCE in MIN_DELAY / 2 than unlock mouse

    if mouseLock and mouseIsUp and (
            (event.Time - lastClickUpTime > MIN_DELAY) or
            (event.Time - lastClickUpTime > MIN_DELAY / 2 and get_distance(
                event.Position, lastClickRealDownPos) <= MIN_DISTANCE)
    ):
        print(event.Time, event.Time - lastClickUpTime, get_distance(event.Position, lastClickRealDownPos))
        mouse_up(hm, lastClickUpPos)
        mouseLock = False
    if event.Message == UP:
        print(event.Time, 'up')
        mouseIsUp = True
        mouseLock = True
        lastClickUpTime = event.Time
        lastClickUpPos = event.Position
        return False
    if event.Message == DOWN:
        print(event.Time, 'down')
        set_high_priority()
        mouseIsUp = False
        if not mouseLock:
            mouseLock = True
            lastClickRealDownPos = event.Position
            print(event.Time, 'true down')
            return True
        else:
            return False
    return True

# set high priority
set_high_priority()

# create a hook manager
hm = pyHook.HookManager()
# watch for all mouse events
hm.MouseAll = on_mouse_event
# set the hook
hm.HookMouse()
# wait forever
pythoncom.PumpMessages()
