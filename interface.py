from config import GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, SAVE_FILE_NAME
from tiles import TileType, get_tile
from console import Console
import json
import os


class UserInterface:
    saved: bool = False
    game: 'Game'
    current_menu_option: int = 0
    schema_choosing: bool = True

    @property
    def menu_options(self) -> list:
        if self.schema_choosing:
            return [
                ("EMOJI", self.set_schema),
                ("ASCII", self.set_schema),
            ]
        if not self.game.game_over:
            return [
                ("CONTINUE", self.continue_game),
                ("SAVE ", self.save_game) if not self.saved else ("SAVED", lambda: True),
                ("LOAD", self.load_game),
                ("EXIT", self.exit)
            ]
        return [
            ("EXIT", self.exit)
        ]

    def set_schema(self):
        self.schema_choosing = False
        self.game.set_schema(self.current_menu_option)


    def continue_game(self) -> None:  # noqa
        self.clear_bottom_area()
        self.game.continue_game()

    def pause_game(self) -> None:  # noqa
        self.game.pause_game()

    def exit(self) -> None:  # noqa
        self.game.exit()

    def save_game(self) -> None:
        if not os.path.exists("saves"):
            os.mkdir("saves")
        save_name = SAVE_FILE_NAME
        data = self.game.dump()
        with open(os.path.join("saves", save_name), "w") as f:
            json.dump(data, f)

        self.saved = True

    def load_game(self) -> None:  # noqa
        save_name = SAVE_FILE_NAME
        with open(os.path.join("saves", save_name)) as f:
            data = json.loads(f.read())
            self.game.load(data)

    def update_right_panel(self) -> None:  # noqa
        lines = [" -=  PLAYER   =-"]
        health_indicator = get_tile(TileType.HEALTH) * self.game.player.health + \
                           get_tile(TileType.HEALTH_EMPTY) * \
                           (self.game.player.max_health - self.game.player.health)
        lines.append("HEALTH: " + health_indicator)

        water_indicator = get_tile(TileType.WATER_TANK) * self.game.player.water_tank + \
                          get_tile(TileType.WATER_TANK_EMPTY) * \
                          (self.game.player.water_tank_capacity - self.game.player.water_tank)
        lines.append("WATER:  " + water_indicator)

        if self.game.player.level >= self.game.player.max_levels:
            exp = f"MAX"
        elif self.game.player.next_level_experience - self.game.player.experience > 0:
            exp = f"{self.game.player.experience}/{self.game.player.next_level_experience}".ljust(7, " ")
        else:
            exp = f"LVL UP!"
        lines.append("EXP:    " + exp)

        lines.append("NEXT UPGRADE:")
        next_upgrades = self.game.player.next_upgrades()
        if next_upgrades:
            for upgrade in next_upgrades:
                lines.append("+" + upgrade.name.ljust(10, " "))
        else:
            lines.append(" MAX")
        lines.append("")
        lines.append(" -=   TREES   =-")
        lines.append(f"SAVED:  {self.game.game_field.total_saved_trees}")
        lines.append(f"BURNED: {self.game.game_field.total_burned_trees}")
        lines.append("")
        lines.append(" -= GAME INFO =-")
        lines.append(f"TICKS:  {self.game.ticks}" + "     ")
        lines.append(f"TPS:    {int(1 // self.game.tick_timedelta)}" + "  ")
        ui_text = "".join([Console.format(line, GAME_FIELD_WIDTH + 2, i) for i, line in enumerate(lines)])
        Console.print_prepared(ui_text)

    @staticmethod
    def clear_bottom_area() -> None:
        for i in range(5):
            Console.print(" " * GAME_FIELD_WIDTH * 2, 0, GAME_FIELD_HEIGHT + i)

    def choice_next_menu_option(self):
        if self.current_menu_option < len(self.menu_options) - 1:
            self.current_menu_option += 1
            self.update_menu()

    def choice_prev_menu_option(self):
        if self.current_menu_option > 0:
            self.current_menu_option -= 1
            self.update_menu()

    def choose_menu_option(self):
        name, func = self.menu_options[self.current_menu_option]
        func()
        if func != self.continue_game and func != self.exit:
            self.update_menu()

    def update_menu(self):
        self.clear_bottom_area()
        options = self.menu_options
        if self.schema_choosing:
            y = 2
        else:
            y = GAME_FIELD_HEIGHT + 2
        Console.print(
            "  ".join([(">" if self.current_menu_option == i else " ") + name for i, (name, _) in enumerate(options)]),
            3, y)
