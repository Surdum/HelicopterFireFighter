## What is it?

There is a little game for university project

## Installing

This game was developed using Python 3.11. Support for earlier versions is not guaranteed.

Poetry:

``
poetry install --no-root
``

OR

PIP:

``
pip install -r requirements.txt
``

AND

Windows Terminal (with other terminals there may be problems with displaying emojis)

```
https://apps.microsoft.com/detail/9n0dx20hk701?activetab=pivot%3Aoverviewtab&hl=en-us&gl=US

or

https://github.com/microsoft/terminal/releases/tag/v1.19.10821.0
```

## Launch

``
poetry run python main.py
OR
python main.py
``

## Playing

Use the arrows to move the helicopter (🚁). You need to put out emerging fires (🔥). 
To do this, you need to fly over the cell with water (🟦) and go to the cell with fire (🔥). 
When you put out enough fires, an upgrade will unlock. To use it, fly over the shop (🛒).

At the third level, after receiving a second life, clouds (☁) appear, partially hiding the field. 
Lightning (⚡) in these clouds causes damage to the player, so it is worth dodging them. 
If the damage has passed, then you need to go to the hospital (🏥).

The game generates a new map every time you start it. 
To save the current result, press SPACE key and select SAVE option. 
To load the result, you need to select the LOAD option in the same menu.
There is only one save slot.

**For better display, install a dark theme on your terminal app.**
