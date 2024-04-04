from generators.base import Generator
from tiles import TileType, buildings


class AloneBuildingGenerator(Generator):
    _tile = TileType.NOTHING
    _entity = "building"

    def run(self, tiles: dict[tuple, TileType]) -> [int, int, TileType]:
        ...

    def find_building_place(self, tiles):
        counter = 0
        x, y = self.find_empty_cell(tiles)
        cells = self.what_around_cell(x, y, tiles)
        while not all([tile != TileType.WATER and
                       tile != TileType.OUT_OF_GAME_FIELD and
                       tile not in buildings
                       for tile in cells.values()]):
            x, y = self.find_empty_cell(tiles)
            cells = self.what_around_cell(x, y, tiles)
            counter += 1
        return x, y


class HospitalGenerator(AloneBuildingGenerator):
    _tile: TileType = TileType.HOSPITAL

    def run(self, tiles: dict[tuple, TileType]) -> [int, int, TileType]:
        building_coordinates = self.find_building_place(tiles)
        for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            yield building_coordinates[0] + direction[0], building_coordinates[1] + direction[1], TileType.NOTHING
        yield *building_coordinates, self.tile


class UpgradeShopGenerator(AloneBuildingGenerator):
    _tile: TileType = TileType.SHOP

    def run(self, tiles: dict[tuple, TileType]) -> [int, int, TileType]:
        building_coordinates = self.find_building_place(tiles)
        for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            yield building_coordinates[0] + direction[0], building_coordinates[1] + direction[1], TileType.NOTHING
        yield *building_coordinates, self.tile
