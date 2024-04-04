from tiles import TileType
from config import GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT, TICK_TIME
from utils import DumpLoad
import time


class GameObject:
    tile_type: TileType
    x: int
    y: int
    moved: bool

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.moved = False

    @property
    def coordinates(self):
        return self.x, self.y


class MovableObject(GameObject):
    last_move_time: float = 0.
    speed: float = 1.  # delay in seconds

    def move(self, shift_x: int, shift_y: int) -> bool:
        if self.x + shift_x >= GAME_FIELD_WIDTH or self.x + shift_x < 0:
            return False
        if self.y + shift_y >= GAME_FIELD_HEIGHT or self.y + shift_y < 0:
            return False
        if time.monotonic() - self.last_move_time > self.speed and not self.moved:
            self.x = self.x + shift_x
            self.y = self.y + shift_y
            self.moved = True
            self.last_move_time = time.monotonic()
            return True
        return False

    def move_up(self) -> bool:
        return self.move(0, -1)

    def move_down(self) -> bool:
        return self.move(0, 1)

    def move_left(self) -> bool:
        return self.move(-1, 0)

    def move_right(self) -> bool:
        return self.move(1, 0)


class Player(MovableObject, DumpLoad):
    tile_type = TileType.HELICOPTER
    speed: float = 0.15  # delay in seconds
    water_tank: int = 0
    water_tank_capacity: int = 1
    health: int = 1
    max_health: int = 1
    experience: int = 0
    next_level_experience: int = 8
    level: int = 1
    max_levels: int = 10
    base_level_cost: int = 10
    level_cost_multiplier: float = 1.
    damage_cooldown: float = 3.
    last_damage_ts: float = 0.
    transparent_skin: bool = False

    fields_to_dump_load = ["tile_type", "speed", "water_tank", "water_tank_capacity",
                           "health", "max_health", "experience", "next_level_experience",
                           "level", "max_levels", "base_level_cost", "level_cost_multiplier",
                           "x", "y"]

    def is_here(self, x: int, y: int) -> bool:
        return self.x == x and self.y == y

    def blink_if_damaged(self) -> bool:
        if time.monotonic() < self.damage_cooldown + self.last_damage_ts:
            self.transparent_skin = not self.transparent_skin
            return True
        else:
            if self.transparent_skin:
                self.transparent_skin = False
                return True
        return False

    @property
    def levels(self) -> list[tuple]:
        return [
            (lambda x: x, ),  # zero level
            (self.upgrade_water_tank_capacity, ),
            (self.upgrade_max_health, ),
            (self.upgrade_max_speed, ),
            (self.upgrade_water_tank_capacity, ),
            (self.upgrade_max_health, ),
            (self.upgrade_max_speed, ),
            (self.upgrade_water_tank_capacity, ),
            (self.upgrade_max_health, ),
            (self.upgrade_max_speed, ),
            (self.upgrade_max_speed, ),
        ]

    def heal(self) -> None:
        self.health = self.max_health

    def apply_damage(self) -> None:
        if self.health > 0 and time.monotonic() - self.last_damage_ts > self.damage_cooldown:
            self.health -= 1
            self.last_damage_ts = time.monotonic()

    def is_alive(self) -> bool:
        return self.health > 0

    def fill_water_tanks(self) -> None:
        self.water_tank = self.water_tank_capacity

    def upgrade_water_tank_capacity(self) -> None:
        self.water_tank_capacity += 1
    upgrade_water_tank_capacity.name = "water tank"

    def upgrade_max_health(self) -> None:
        self.max_health += 1
        self.health = self.max_health
    upgrade_max_health.name = "health"

    def upgrade_max_speed(self) -> None:
        self.speed *= 0.8
    upgrade_max_speed.name = "speed"

    def next_upgrades(self) -> tuple:
        if self.level < self.max_levels:
            return self.levels[self.level]
        return []

    def level_up(self) -> bool:
        if self.level >= self.max_levels:
            return False
        if self.next_level_experience > self.experience:
            return False
        upgrades = self.next_upgrades()
        for upgrade in upgrades:
            upgrade()
        self.level += 1
        self.experience -= self.next_level_experience
        self.level_cost_multiplier *= 1.5
        self.next_level_experience = int(self.base_level_cost * self.level_cost_multiplier)
        return True
