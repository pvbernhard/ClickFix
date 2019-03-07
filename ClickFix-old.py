from typing import Tuple

import psutil
import os

import math

import pythoncom
import pyWinhook as pyHook

import ctypes


# MessageName : mouse move
# Message : 512
# MessageName : mouse left down
# Message : 513
# MessageName : mouse left up
# Message : 514

MIN_DELAY: int = 150                            # ms
MIN_DISTANCE: int = 9                           # px

lastClickRealDownPos: Tuple[int, int] = (0, 0)      # x, y
mouseState: str = 'up'                          # 'up', 'down'
mouseStateInSelection: str = 'down'             # 'down', 'up'
mouseIsSelecting: bool = False
lastClickUpTime: int = 0
lastClickUpSelectPos: Tuple[int, int] = (0, 0)
lastClickUpSelectTime: int = 0
lastClickDownBug: bool = False                  # down-up bug outside selection


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


def sethighprio():
    # set high priority
    p = psutil.Process(os.getpid())
    # print('> prio before', int(p.nice()))
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    # print('> prio after', int(p.nice()))


def get_distance(pos_1, pos_2):
    return math.sqrt((pos_2[0] - pos_1[0])**2 + (pos_2[1] - pos_1[1])**2)


def mouse_up(hndl, pos):
    # ctypes.windll.user32.SetCursorPos(x, y)
    hndl.UnhookMouse()
    import win32con
    # pos = ctypes.windll.user32.GetCursorPos()
    ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTUP, pos[0], pos[1], 0, 0)
    # print('mouse_up')
    hndl.HookMouse()


def onmouseevent(event):
    global hm

    global MIN_DELAY
    global MIN_DISTANCE

    global lastClickRealDownPos
    global mouseState
    global mouseStateInSelection
    global mouseIsSelecting
    global lastClickUpTime
    global lastClickUpSelectPos
    global lastClickUpSelectTime
    global lastClickDownBug

    # called when mouse events are received
    # messages(event)

    # print(event.Time, mouseState, mouseIsSelecting, mouseStateInSelection,
    # get_distance(lastClickDownPos, event.Position), event.Message)

    if get_distance(lastClickRealDownPos, event.Position) > MIN_DISTANCE and mouseState == 'down':
        mouseIsSelecting = True
    else:
        mouseIsSelecting = False

    if not mouseIsSelecting:
        # mouse down
        if event.Message == 513:
            if event.Time - lastClickUpTime > MIN_DELAY:
                lastClickRealDownPos = event.Position
                mouseState = 'down'

                # set high priority when clicking
                sethighprio()

                return True
            else:
                # print('bug down')
                lastClickDownBug = True
                return False
        # mouse up
        if event.Message == 514:
            if lastClickDownBug:
                # consume the down-up bug
                # print('bug up')
                lastClickDownBug = False
                return False
            else:
                lastClickUpTime = event.Time
                mouseState = 'up'
                return True
    else:  # mouse is selecting
        # mouse down
        if event.Message == 513:
            mouseStateInSelection = 'down'
            return False
        # mouse up
        if event.Message == 514:
            mouseStateInSelection = 'up'
            lastClickUpSelectPos = event.Position
            lastClickUpSelectTime = event.Time
            return False
        # free selecting
        if mouseStateInSelection == 'up' and event.Time - lastClickUpSelectTime > MIN_DELAY * 1.3:
            # print(event.Time - lastClickUpSelectTime)
            mouseIsSelecting = False
            mouseStateInSelection = 'down'  # reset the default value
            lastClickUpTime = lastClickUpSelectTime
            mouseState = 'up'
            mouse_up(hm, lastClickUpSelectPos)
            return True
    return True


# set high priority
sethighprio()

# create a hook manager
hm = pyHook.HookManager()
# watch for all mouse events
hm.MouseAll = onmouseevent
# set the hook
hm.HookMouse()
# wait forever
pythoncom.PumpMessages()
