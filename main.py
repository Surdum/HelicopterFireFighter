from generators import *
from tiles import TileType, get_tile, Layers, get_layer
from console import Console
from config import *

from utils import DumpLoad
from interface import UserInterface

from objects import Player
from collections import defaultdict
from random import choice, randint, random
from pynput import keyboard
import time


game: 'Game' = None


class ExitException(BaseException):
    ...


class Controller:
    controller: keyboard.Controller = keyboard.Controller()
    listener: keyboard.Listener
    ignore_input: bool = False
    pressed: dict = {}

    def on_press(self, key: keyboard.Key) -> None:
        if self.ignore_input:
            return
        self.pressed[key] = True

    def on_release(self, key: keyboard.Key) -> None:
        # if hasattr(key, 'char') and key.char == 'k':
        #     game.player.apply_damage()

        if key in self.pressed:
            del self.pressed[key]

        if key == keyboard.Key.space:
            if game.paused:
                game.continue_game()
            else:
                game.pause_game()
        if game.paused:
            if key == keyboard.Key.left:
                game.ui.choice_prev_menu_option()
            elif key == keyboard.Key.right:
                game.ui.choice_next_menu_option()
            elif key == keyboard.Key.enter:
                game.ui.choose_menu_option()

    def listen(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            suppress=True,
        )
        self.listener.start()


class GameField(DumpLoad):
    ground_tiles: dict[tuple, TileType] = {}
    fire_tiles: dict[tuple, float] = {}
    cloud_tiles: dict[tuple, TileType] = {}

    spark_chance_modifier: float = 1.
    current_spark_chance_modifier: float = 1.

    tree_growing_chance_modifier: float = 1.
    buildings: dict[TileType, list] = defaultdict(list)

    total_saved_trees: int = 0
    total_burned_trees: int = 0

    empty_cell: tuple = None
    grow_next_tree: bool = False

    last_clouds_movement_ts: float = 0.

    fields_to_dump_load = ["ground_tiles", "fire_tiles", "cloud_tiles",
                           "spark_chance_modifier", "current_spark_chance_modifier",
                           "tree_growing_chance_modifier", "buildings", "total_saved_trees",
                           "total_burned_trees", "empty_cell", "grow_next_tree"]

    def __init__(self):
        self._stat = self.Statistic()

    @staticmethod
    def is_coordinates_in_field(x, y):
        return (0 <= x < GAME_FIELD_WIDTH) and (0 <= y < GAME_FIELD_HEIGHT)

    def generate(self, generator: 'Generator') -> None:
        if generator.entity == "fire":
            tiles = self.fire_tiles
        elif generator.entity == "cloud":
            tiles = self.cloud_tiles
        else:
            tiles = self.ground_tiles
        for x, y, tile in generator.run(tiles):
            if generator.entity == "building" and tile != TileType.NOTHING:
                self.buildings[tile].append((x, y))
            if tile != TileType.NOTHING:
                layer = get_layer(tile)
                display = (x >= 0)
                self.add_element(x, y, tile, layer=layer, display=display)
            else:
                self.remove_element(x, y)
            if SMOOTH_GENERATION:
                time.sleep(GENERATION_SLOWDOWN)

    @property
    def stat(self):
        return self._stat

    def fill(self, x: int, y: int, width: int, height: int, tile_type: TileType) -> None:  # noqa
        filler = [[get_tile(tile_type) for _ in range(width)] for _ in range(height)]
        Console.print("\n".join(["".join(line) for line in filler]), x, y)

    def add_element(self, x: int, y: int, tile_type: TileType = None, layer: int = Layers.GROUND,
                    only_visual: bool = False, display: bool = True) -> None:
        if isinstance(get_tile(tile_type), (tuple, list)):
            tile = choice(get_tile(tile_type))
        else:
            tile = get_tile(tile_type)
        if display:
            Console.print(tile, x, y)
        if not only_visual:
            if layer == Layers.GROUND:
                tile_layer = self.ground_tiles
            elif layer == Layers.FIRE:
                tile_layer = self.fire_tiles
            elif layer == Layers.SKY:
                tile_layer = self.cloud_tiles
            else:
                raise
            if tile_type != TileType.FIRE:
                tile_layer[(x, y)] = tile_type
            else:
                tile_layer[(x, y)] = time.monotonic()
            self.stat.occupied += TILE_COST
            if tile_type == TileType.TREE:
                self.stat.trees_ratio += TILE_COST
                self.stat.trees += 1
            elif tile_type == TileType.WATER:
                self.stat.water_ratio += TILE_COST

    def remove_element(self, x: int, y: int, layer: int = Layers.GROUND):
        if layer == Layers.GROUND:
            tiles = self.ground_tiles
        elif layer == Layers.FIRE:
            tiles = self.fire_tiles
        elif layer == Layers.SKY:
            tiles = self.cloud_tiles
        else:
            raise
        if (x, y) in tiles:
            del tiles[(x, y)]
            self.redraw_element(x, y)

    def redraw_element(self, x: int, y: int) -> None:
        if (x, y) == game.player.coordinates and not game.player.transparent_skin:
            self.add_element(x, y, game.player.tile_type, only_visual=True)
        elif (x, y) in self.cloud_tiles:
            self.add_element(x, y, self.cloud_tiles[(x, y)], only_visual=True)
        elif (x, y) in self.fire_tiles:
            self.add_element(x, y, TileType.FIRE, only_visual=True)
        elif (x, y) in self.ground_tiles:
            self.add_element(x, y, self.ground_tiles[(x, y)], only_visual=True)
        else:
            self.add_element(x, y, TileType.GROUND, only_visual=True)

    def throw_a_spark(self):
        if random() > BASE_SPARK_CHANCE * self.spark_chance_modifier:
            if not self.fire_tiles:
                self.spark_chance_modifier *= 1.5
            return False
        self.spark_chance_modifier = self.current_spark_chance_modifier
        target = choice(list(self.ground_tiles.keys()))
        while self.ground_tiles[target] != TileType.TREE:
            target = choice(list(self.ground_tiles.keys()))
        return target

    def spread_fire(self) -> list[tuple]:
        new_fire_coordinates = []
        for fire_coordinates in self.fire_tiles:
            if random() > BASE_FIRE_SPREAD_CHANCE:
                continue
            not_burning_trees_around = []
            for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                coordinates = fire_coordinates[0] + direction[0], fire_coordinates[1] + direction[1]
                if self.fire_tiles.get(coordinates, None) is None and \
                        self.ground_tiles.get(coordinates, None) == TileType.TREE:
                    not_burning_trees_around.append(coordinates)
            if not not_burning_trees_around:
                continue
            new_fire_coordinates.append(choice(not_burning_trees_around))
        return new_fire_coordinates

    def grow_a_tree(self) -> tuple:
        if self.empty_cell is not None:
            if random() > BASE_TREE_CHANCE:
                return False
            self.grow_next_tree = False
            target = self.empty_cell
            self.empty_cell = None
            return target
        target = (randint(0, GAME_FIELD_WIDTH - 1), randint(0, GAME_FIELD_HEIGHT - 1))
        if self.ground_tiles.get(target, TileType.ASH) == TileType.ASH:  # grow on empty cell or ash
            self.empty_cell = target
        return False

    def make_ashes(self) -> list[tuple]:
        burned = []
        for coordinates, start_time in self.fire_tiles.items():
            if start_time + 5. < time.monotonic():
                burned.append(coordinates)
        self.total_burned_trees += len(burned)
        return burned

    def extinguish_tree(self, x: int, y: int) -> None:
        self.total_saved_trees += 1
        del self.fire_tiles[(x, y)]

    def redraw_game_field(self) -> None:
        for x in range(GAME_FIELD_WIDTH):
            for y in range(GAME_FIELD_HEIGHT):
                self.redraw_element(x, y)

    def game_over(self):
        game.game_over = True
        game.pause_game()
        self.add_element(*game.player.coordinates, TileType.DEATH, only_visual=True, layer=2)
        Console.print(" " * (GAME_FIELD_WIDTH * 2), 0, GAME_FIELD_HEIGHT // 2 - 1)
        Console.print(" " * (GAME_FIELD_WIDTH * 2), 0, GAME_FIELD_HEIGHT // 2)
        Console.print(" " * (GAME_FIELD_WIDTH * 2), 0, GAME_FIELD_HEIGHT // 2 + 1)
        Console.print("GAME OVER", GAME_FIELD_WIDTH // 2 - 2, GAME_FIELD_HEIGHT // 2)

    def move_clouds(self):
        if self.cloud_tiles and self.last_clouds_movement_ts + CLOUD_SPEED < time.monotonic():
            old_coordinates = set(self.cloud_tiles)
            self.cloud_tiles = {(k[0] + 1, k[1]): v for k, v in self.cloud_tiles.items()}
            new_coordinates = set(self.cloud_tiles)
            self.last_clouds_movement_ts = time.monotonic()
            for coordinates in new_coordinates | old_coordinates:
                if coordinates[0] >= GAME_FIELD_WIDTH:
                    del self.cloud_tiles[coordinates]
                elif coordinates[0] >= 0 and 0 <= coordinates[1] < GAME_FIELD_HEIGHT:
                    self.redraw_element(*coordinates)

    def make_clouds(self):
        if game.player.level >= 3 and len(self.cloud_tiles) < 5:
            for _ in range(1, 4):
                self.generate(CloudGenerator(max_limit=randint(6, 20)))

    class Statistic:
        occupied = 0
        water = 0
        water_ratio = 0.
        trees = 0
        trees_ratio = 0.


class Game(DumpLoad):
    ticks: int = 0
    last_tick_ts: float = 0.
    tick_timedelta: float = 0.
    game_field: GameField
    player: Player
    listener: keyboard.Listener
    controller: Controller
    ui: UserInterface
    paused: bool = False
    pause_ts: float = 0.
    playing: bool = True
    game_over: bool = False

    fields_to_dump_load = ["ticks", "last_tick_ts", "pause_ts"]

    def pause_game(self):
        self.paused = True
        self.pause_ts = time.monotonic()
        self.ui.update_menu()

    def continue_game(self):
        ts = time.monotonic() + 0.1
        for tile in self.game_field.fire_tiles:
            self.game_field.fire_tiles[tile] += ts - self.pause_ts
        self.paused = False
        self.ui.clear_bottom_area()

    def dump(self) -> dict:
        data = super().dump()
        data["game_field"] = self.game_field.dump()
        data["player"] = self.player.dump()
        return data

    def load(self, data):
        super(Game, self).load(data)
        self.game_field.load(data["game_field"])
        self.player.load(data["player"])
        self.game_field.redraw_game_field()

    def init(self):
        Console.clear_screen()
        self.game_field = GameField()
        self.player = Player(GAME_FIELD_WIDTH // 2, GAME_FIELD_HEIGHT // 2)
        self.ui = UserInterface()
        self.ui.game = self
        self.controller = Controller()
        #
        self.game_field.fill(0, 0, GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT, TileType.GROUND)
        #
        self.game_field.generate(LakeGenerator(max_limit=randint(10, 20)))
        self.game_field.generate(LakeGenerator(max_limit=randint(10, 20)))
        #
        if self.game_field.stat.water_ratio < WATER_FREQUENCY:
            self.game_field.generate(RiverGenerator(max_limit=200))
        #
        while self.game_field.stat.trees_ratio < FOREST_FREQUENCY:
            self.game_field.generate(ForestGenerator(max_limit=randint(4, 7)))
        #
        self.game_field.generate(HospitalGenerator())
        self.game_field.generate(UpgradeShopGenerator())
        #
        self.game_field.add_element(*self.player.coordinates, self.player.tile_type, only_visual=True)

        self.controller.listen()

    def game_tick(self):
        # move clouds
        self.game_field.move_clouds()
        # player movement
        player_x = self.player.x
        player_y = self.player.y
        if ControlSchema.UP in self.controller.pressed:
            self.player.move_up()
        elif ControlSchema.DOWN in self.controller.pressed:
            self.player.move_down()
        elif ControlSchema.LEFT in self.controller.pressed:
            self.player.move_left()
        elif ControlSchema.RIGHT in self.controller.pressed:
            self.player.move_right()
        if self.player.moved:
            self.game_field.add_element(self.player.x, self.player.y, self.player.tile_type, only_visual=True)
            self.game_field.redraw_element(player_x, player_y)
            self.player.moved = False
            # water
            if self.game_field.ground_tiles.get(self.player.coordinates) == TileType.WATER:
                self.player.fill_water_tanks()
            # hospital
            elif self.game_field.ground_tiles.get(self.player.coordinates) == TileType.HOSPITAL:
                self.player.heal()
            # upgrade shop
            elif self.game_field.ground_tiles.get(self.player.coordinates) == TileType.SHOP:
                if self.player.level_up():
                    self.game_field.current_spark_chance_modifier *= 1.1
            # extinguish
            elif self.game_field.fire_tiles.get(self.player.coordinates):
                if self.player.water_tank > 0:
                    self.game_field.extinguish_tree(*self.player.coordinates)
                    self.player.water_tank -= 1
                    self.player.experience += 1
        # lightning damage
        if self.game_field.cloud_tiles.get(self.player.coordinates) == TileType.LIGHTNING:
            self.player.apply_damage()
        # is player alive
        if not self.player.is_alive():
            self.game_field.game_over()
        # blink if damaged
        if self.player.blink_if_damaged():
            self.game_field.redraw_element(*self.player.coordinates)
        # grow tree
        coordinates = self.game_field.grow_a_tree()
        if coordinates:
            self.game_field.add_element(*coordinates, TileType.TREE, layer=get_layer(TileType.TREE),
                                        display=not self.player.is_here(*coordinates))
        # make fire
        coordinates = self.game_field.throw_a_spark()
        if coordinates:
            self.game_field.add_element(*coordinates, TileType.FIRE, layer=get_layer(TileType.FIRE),
                                        display=not self.player.is_here(*coordinates))
        # spread fire
        new_fire_coordinates = self.game_field.spread_fire()
        for coordinates in new_fire_coordinates:
            self.game_field.add_element(*coordinates, TileType.FIRE, layer=get_layer(TileType.FIRE),
                                        display=not self.player.is_here(*coordinates))
        # removing burned trees
        burned_trees = self.game_field.make_ashes()
        for coordinates in burned_trees:
            if self.game_field.ground_tiles.get(coordinates):
                del self.game_field.ground_tiles[coordinates]
            if self.game_field.fire_tiles.get(coordinates):
                del self.game_field.fire_tiles[coordinates]
            self.game_field.ground_tiles[coordinates] = TileType.ASH
            if coordinates != self.player.coordinates:
                self.game_field.redraw_element(*coordinates)
        # make clouds
        self.game_field.make_clouds()
        #
        self.ui.saved = False
        self.ui.burned_trees = self.game_field.total_burned_trees
        self.ui.saved_trees = self.game_field.total_saved_trees

    def exit(self):
        self.playing = False
        self.controller.listener.stop()

    def tick(self):
        if not self.paused:
            self.game_tick()
        self.tick_timedelta = time.monotonic() - self.last_tick_ts
        self.ticks += 1
        self.ui.update_right_panel()
        self.last_tick_ts = time.monotonic()

    def run(self):
        self.init()
        while self.playing:
            self.tick()
            time.sleep(TICK_TIME)
        self.controller.listener.stop()
        Console.clear_screen()


if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        Console.clear_screen()
        ...
