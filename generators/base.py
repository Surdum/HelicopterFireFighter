from config import GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from tiles import TileType
import random


class Generator:
    _tile: TileType = NotImplemented
    _entity: str = NotImplemented

    def __init__(self, max_limit: int = 10):
        self.max_limit = max_limit

    @property
    def tile(self):
        if isinstance(self._tile, (tuple, list, set)):
            return random.choice(self._tile)
        return self._tile

    @property
    def entity(self):
        return self._entity

    def run(self, tiles: dict[tuple, TileType]) -> [int, int, TileType]:
        raise NotImplementedError

    def spread(self, x: int, y: int, tiles: dict[tuple, TileType]) -> [int, int]:
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        visited_points = set()
        points = {(x, y)}
        tile_count = 0
        while points:
            x_, y_ = points.pop()
            for offset_x, offset_y in directions:
                new_x, new_y = x_ + offset_x, y_ + offset_y
                if new_x < 0 or new_x >= GAME_FIELD_WIDTH or \
                        new_y < 0 or new_y >= GAME_FIELD_HEIGHT or \
                        (new_x, new_y) in visited_points:
                    continue
                if tiles.get((new_x, new_y), None) is None:
                    visited_points.add((new_x, new_y))
                    yield new_x, new_y
                    points.add((new_x, new_y))
                    tile_count += 1
                if tile_count >= self.max_limit:
                    return

    def find_empty_cell(self, tiles: dict[tuple, TileType]) -> [int, int]:  # noqa
        x, y = random.randint(0, GAME_FIELD_WIDTH - 1), random.randint(0, GAME_FIELD_HEIGHT - 1)
        while (x, y) in tiles:
            x, y = random.randint(0, GAME_FIELD_WIDTH - 1), random.randint(0, GAME_FIELD_HEIGHT - 1)
        return x, y

    def is_cell_empty(self, x: int, y: int, tiles: dict[tuple, TileType]) -> bool:  # noqa
        return (x, y) not in tiles

    def what_around_cell(self, x: int, y: int, tiles: dict[tuple, TileType]) -> dict[tuple, TileType]:  # noqa
        cells = {}
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue
                new_x = x + i
                new_y = y + j
                if new_x < 0 or new_y < 0 or new_x >= GAME_FIELD_WIDTH or new_y >= GAME_FIELD_HEIGHT:
                    cells[(new_x, new_y)] = TileType.OUT_OF_GAME_FIELD
                else:
                    cells[(new_x, new_y)] = tiles.get((new_x, new_y), TileType.NOTHING)
        return cells
