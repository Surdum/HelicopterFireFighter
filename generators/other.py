from generators.base import Generator
from config import GENERATION_SLOWDOWN, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from tiles import TileType
import random
import time


class RiverGenerator(Generator):
    _tile: TileType = TileType.WATER
    _entity = "water"

    def make_river(self) -> [int, int, TileType]:
        points = set()
        direction = random.randint(0, 1)
        if direction == 0:
            start_point = (random.randint(0, GAME_FIELD_WIDTH - 1), 0)
        else:
            start_point = (0, random.randint(0, GAME_FIELD_HEIGHT - 1))
        current_point = start_point
        yield current_point[0], current_point[1]
        points.add(current_point)
        tile_count = 1
        while True:
            if direction == 0:
                k = random.random()
                if k < 0.6:
                    current_point = (current_point[0], current_point[1] + 1)
                else:
                    if k < 0.8:
                        current_point = (current_point[0] + 1, current_point[1])
                    else:
                        current_point = (current_point[0] - 1, current_point[1])
                    if current_point in points:
                        continue
            elif direction == 1:
                k = random.random()
                if k < 0.6:
                    current_point = (current_point[0] + 1, current_point[1])
                else:
                    if k < 0.8:
                        current_point = (current_point[0], current_point[1] + 1)
                    else:
                        current_point = (current_point[0], current_point[1] - 1)
                    if current_point in points:
                        continue
            if current_point[1] >= GAME_FIELD_HEIGHT:
                break
            if current_point[0] >= GAME_FIELD_WIDTH:
                break
            if current_point[1] < 0 or current_point[0] < 0:
                break
            if tile_count >= self.max_limit:
                return
            points.add(current_point)
            yield current_point[0], current_point[1]
            tile_count += 1
            time.sleep(GENERATION_SLOWDOWN)

    def run(self, tiles: dict[tuple, TileType]):
        for x_, y_ in self.make_river():
            yield x_, y_, self.tile


class LakeGenerator(Generator):
    _tile: TileType = TileType.WATER
    _entity = "water"

    def run(self, tiles: dict[tuple, TileType], stop_func: callable = None) -> [int, int, TileType]:
        x, y = (random.randint(1, GAME_FIELD_WIDTH - 2), random.randint(1, GAME_FIELD_HEIGHT))
        for x_, y_ in self.spread(x, y, tiles):
            yield x_, y_, self.tile


class ForestGenerator(Generator):
    _tile: TileType = TileType.TREE
    _entity = "tree"

    def run(self, tiles: dict[tuple, TileType]) -> [int, int, TileType]:
        x, y = (random.randint(1, GAME_FIELD_WIDTH - 2), random.randint(1, GAME_FIELD_HEIGHT))
        for x_, y_ in self.spread(x, y, tiles):
            yield x_, y_, self.tile


class CloudGenerator(Generator):
    _tile: TileType = TileType.CLOUD
    _entity = "cloud"

    def run(self, tiles: dict[tuple, TileType]) -> [int, int, TileType]:
        x, y = int(GAME_FIELD_WIDTH // 2), int(GAME_FIELD_HEIGHT // 2)

        cloud_coordinates = list(self.spread(x, y, tiles))
        right_point = max(cloud_coordinates, key=lambda item: item[0])
        lightning_count = random.randint(0, len(cloud_coordinates) // 5)
        lightning_indexes = {random.randint(0, len(cloud_coordinates) - 1) for _ in range(lightning_count)}
        indentation_x = random.randint(1, 6)
        indentation_y = random.randint(-GAME_FIELD_HEIGHT, GAME_FIELD_HEIGHT) // 2
        for i, (x, y) in enumerate(cloud_coordinates):
            tile = TileType.LIGHTNING if i in lightning_indexes else self.tile
            yield x - right_point[0] - indentation_x, y + indentation_y, tile




