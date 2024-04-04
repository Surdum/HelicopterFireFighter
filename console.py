import os
import sys


class Console:
    @staticmethod
    def format(text: str, x: int, y: int) -> str:
        return f"\033[{y+1};{x*2+1}H{text}"

    @staticmethod
    def print(text: str, x: int, y: int) -> None:
        print(Console.format(text, x, y))

    @staticmethod
    def print_prepared(text: str) -> None:
        print(text)

    @staticmethod
    def clear_screen() -> None:
        if sys.platform == "win32":
            os.system('cls')
        else:
            os.system('clear')

