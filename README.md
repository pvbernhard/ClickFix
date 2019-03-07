# Click Fix

A little python script I made to fix my mouse issues with random clicks.

## About the bug

My mouse was behaving strangely: everytime I clicked, it would randomly click one, two or even three more times. Also, when I tried toclick and drag (to select a text or drag a file) the mouse would randomly lose focus and sometimes double clicking right after.

So, after some debugging, that was what I found how the bug behaved:

- When holding the left click, the mouse sends a DOWN signal. The bug makes the mouse send UP signals randomly while holding.
- When letting go of the mouse, the mouse sends an UP signal. The bug makes the mouse send a DOWN signal right after, followed by an UP signal (sometimes more than once).

Yeah, but why?

After some tests, I found out that it's not the mouse in particular (probably... I tested 3 different mouses; maybe I'm just unlucky) and it's not the OS (I tested both in Windows 10 and Ubuntu 18.04). So I still have no idea what's happening, but I suspect the CMOS battery of my notebook.

If you have a similar problem you might find this script useful.

## What the script do?

To put it simple: the script *locks* the mouse after a DOWN signal and then waits for an *actual* UP signal, ignoring any fake DOWN and UP signals.

To know if the signal is a fake or real, the scripts waits a bit to see if the mouse state will change back to DOWN after `MIN_DELAY` milliseconds, if it doesn't it's probably a real signal, if it does then it is most certainly a fake.

To make things a bit more responsive, there's a distinction between *dragging* the mouse and a simple click: if the mouse is still, the script waits less time (`MIN_DELAY` ms); if the mouse is moving, the script waits longer (`MIN_DELAY` times `SELECTION_RATE`).

## Getting Started

There is a binary file in the `dist` folder already if you don't feel like compiling your own.

It was made with `pyinstaller -w -F`.

### Prerequisites

There are no prerequisites to the binary files as far as I know.

The script needs:

- `pythoncom` and `win32con`, both can be installed with this: https://github.com/mhammond/pywin32/releases
    - This is used to send mouse inputs.
- `pyWinhook`, from: https://github.com/Tungsteno74/pyWinhook
    - This is used to read mouse inputs.
- `psutil`, from: https://github.com/giampaolo/psutil
    - This is used to make the process have high priority - so it can hook the mouse before other processes.

### Installing

This is what I do: I have my binary file in a folder in my documents and in the `Startup` folder I have a VBS script to execute the **ClickFix** script with admin privileges. The VBS script is also in the `dist` folder. This was done because I couldn't normally start the script with admin privileges at startup.

## Author

* **Pedro Vinnícius Bernhard**
