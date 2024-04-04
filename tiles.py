import sys


class TileType:
    OUT_OF_GAME_FIELD = -2
    NOTHING = -1
    GROUND = 0
    WATER = 1
    TREE = 2
    FIRE = 3
    ASH = 4
    HOSPITAL = 5
    WHEAT = 6
    HELICOPTER = 7
    HEALTH = 8
    CLOUD = 9
    WATER_TANK = 10
    WATER_TANK_EMPTY = 11
    HEALTH_EMPTY = 12
    SHOP = 13
    LIGHTNING = 14
    DEATH = 15


class _Tiles:
    BLACK_CIRCLE = "⚫"
    WHITE_CIRCLE = "⚪"
    BLUE_CIRCLE = "🔵"
    RED_CIRCLE = "🔴"
    RED_HEART = "❤️"
    BLACK_HEART = "🖤"
    HOSPITAL = "🏥"
    GROUND = "🟫"
    CURSER_GROUND = "🏾"
    WATER = "🟦"
    WAVE = "🌊"
    GRASS = "🟩"
    WHEAT = "🌾"
    TREES = "🌲"  # "🌳"
    FIRE = "🔥"
    ASH = "✶" if sys.platform == "win32" else "🌫"
    HELICOPTER = "🚁"
    SHOP = "🛒"
    CLOUD = "☁" if sys.platform == "win32" else "☁️"
    LIGHTNING = "⚡"  # "🌩️"
    DEATH = "💀"


_tile_mapping = {
    TileType.TREE: _Tiles.TREES,
    TileType.WATER: _Tiles.WATER,
    TileType.GROUND: _Tiles.GROUND,
    TileType.FIRE: _Tiles.FIRE,
    TileType.ASH: _Tiles.ASH,
    TileType.HOSPITAL: _Tiles.HOSPITAL,
    TileType.WHEAT: _Tiles.WHEAT,
    TileType.HELICOPTER: _Tiles.HELICOPTER,
    TileType.NOTHING: _Tiles.GROUND,
    TileType.CLOUD: _Tiles.CLOUD,
    TileType.WATER_TANK: _Tiles.BLUE_CIRCLE,
    TileType.WATER_TANK_EMPTY: _Tiles.BLACK_CIRCLE,
    TileType.HEALTH: _Tiles.RED_HEART,
    TileType.HEALTH_EMPTY: _Tiles.BLACK_HEART,
    TileType.SHOP: _Tiles.SHOP,
    TileType.LIGHTNING: _Tiles.LIGHTNING,
    TileType.DEATH: _Tiles.DEATH,
}


class Layers:
    GROUND = 0
    FIRE = 1
    SKY = 2


_layers = {
    TileType.WATER: Layers.GROUND,
    TileType.TREE: Layers.GROUND,
    TileType.HOSPITAL: Layers.GROUND,
    TileType.SHOP: Layers.GROUND,
    TileType.GROUND: Layers.GROUND,
    #
    TileType.FIRE: Layers.FIRE,
    #
    TileType.CLOUD: Layers.SKY,
    TileType.LIGHTNING: Layers.SKY,
}


buildings = {TileType.HOSPITAL, TileType.SHOP}


def get_tile(tile_type: TileType) -> str:
    return _tile_mapping[tile_type]


def get_layer(tile_type: TileType) -> int:
    return _layers[tile_type]
