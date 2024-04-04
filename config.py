"""
    Config file
"""
from pynput import keyboard


GAME_FIELD_WIDTH = 25
GAME_FIELD_HEIGHT = 15

TILE_COST = 1. / (GAME_FIELD_WIDTH * GAME_FIELD_HEIGHT)

FOREST_FREQUENCY = 0.7
WATER_FREQUENCY = 0.1

SMOOTH_GENERATION = True
GENERATION_SLOWDOWN = 0.005
TICK_TIME = 0.033

BASE_SPARK_CHANCE = 0.007
BASE_FIRE_SPREAD_CHANCE = 0.006
BASE_TREE_CHANCE = 0.005

CLOUD_SPEED = 0.1  # delay in seconds

SAVE_FILE_NAME = "save.json"


# Control schema
class ControlSchema:
    UP = keyboard.Key.up
    DOWN = keyboard.Key.down
    LEFT = keyboard.Key.left
    RIGHT = keyboard.Key.right


