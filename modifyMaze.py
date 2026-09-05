import sys  # type: ignore[import-not-found]
from pathlib import Path
import json

GENERATOR_PATH = (Path(__file__).parent / "mazegenerator-00001"
                  / "mazegenerator-2.1.0-py3-none-any")
if str(GENERATOR_PATH) not in sys.path:
    sys.path.insert(0, str(GENERATOR_PATH))

from mazegenerator import (  # type: ignore[import-not-found] # noqa: E402
    MazeGenerator,
)


# Fixed cherry locations, expressed as (x, y) maze-cell coordinates.
CHERRY_POSITIONS = {
    1: [(1, 1), (12, 1), (1, 12), (12, 12)],
    2: [(1, 1), (12, 1), (1, 12), (12, 12)],
    3: [(1, 1), (14, 1), (1, 14), (14, 14)],
    4: [(1, 1), (14, 1), (1, 14), (14, 14)],
    5: [(1, 1), (16, 1), (1, 16), (16, 16)],
    6: [(1, 1), (16, 1), (1, 16), (16, 16)],
    7: [(1, 1), (18, 1), (1, 18), (18, 18)],
    8: [(1, 1), (18, 1), (1, 18), (18, 18)],
    9: [(1, 1), (20, 1), (1, 20), (20, 20)],
    10: [(1, 1), (20, 1), (1, 20), (20, 20)],
}

with open("config.json", "r") as file:
    config = json.load(file)


class Cell:
    def __init__(self, x, y, walls):
        self.x = x
        self.y = y
        self.North = bool(walls & 1)
        self.East = bool(walls & 2)
        self.South = bool(walls & 4)
        self.West = bool(walls & 8)
        self.wall = walls == 15
        self.pellet = not self.wall
        self.power_pellet = False
        self.pacman = False
        self.ghost = False
        self.visited = False


class LevelMaze:
    def __init__(self, layout):
        self.height = len(layout)
        self.width = len(layout[0])
        self.cells = {
            (x, y): Cell(x, y, layout[y][x])
            for y in range(self.height)
            for x in range(self.width)
        }

    def get_neighbors(self, x, y):
        possible = [
            ("North", x, y - 1),
            ("East", x + 1, y),
            ("South", x, y + 1),
            ("West", x - 1, y),
        ]
        return [
            (direction, self.cells[(neighbor_x, neighbor_y)])
            for direction, neighbor_x, neighbor_y in possible
            if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height
        ]


def create_level_maze(level_number):
    level = config[str(level_number)]
    generator = MazeGenerator(
        size=(level["width"], level["height"]),
        perfect=False,
        seed=level_number + 5,
    )
    maze = LevelMaze(generator.maze)
    for position in CHERRY_POSITIONS[level_number]:
        maze.cells[position].power_pellet = True
        maze.cells[position].pellet = False
    return maze
