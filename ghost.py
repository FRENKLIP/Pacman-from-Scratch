from collections import deque

import pygame  # type: ignore[import-not-found]
from typing import Dict, Tuple, Optional
from player import pacman_size


red_dead = False
blue_dead = False
orange_dead = False
pink_dead = False
red_box = False
blue_box = False
orange_box = False
pink_box = False
eatable_ghost = False
powerup = False
eaten_ghosts = [False, False, False, False]
returned_ghosts = [False, False, False, False]
dead = False


class Ghost:
    def __init__(
            self,
            target: list,
            speed: float,
            img,
            direct,
            dead: bool,
            box: bool,
            id: int,
            lev_num: int,
            ghost: str,
            screen,
            maze,
            offset_x: int,
            offset_y: int,
            ghost_size: tuple[int, int],
            cell_size: int,
            eaten_ghosts: list,
            ):

        self.x_pos, self.y_pos = ghost_position(lev_num, ghost)

        self.center_x = self.x_pos + ghost_size[0] // 2
        self.center_y = self.y_pos + ghost_size[1] // 2
        self.start_x_pos = self.x_pos
        self.start_y_pos = self.y_pos

        self.speed = speed
        self.img = img
        # self.dead_img = dead_img
        # self.power_img = power_img

        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id

        self.target = target
        self.ghost_size = ghost_size

        self.turns, self.in_box = self.check_collision(
            maze,
            offset_x,
            offset_y,
            ghost_size,
            speed,
            cell_size
        )

        self.rect = self.draw(screen, eaten_ghosts, dead)

    def reset_position(self) -> None:
        """Return this ghost to its level-start position."""
        self.x_pos = self.start_x_pos
        self.y_pos = self.start_y_pos
        self.center_x = self.x_pos + self.ghost_size[0] // 2
        self.center_y = self.y_pos + self.ghost_size[1] // 2

    def draw(self, screen, eaten_ghost, dead):
        if ((not powerup or returned_ghosts[self.id]) and not self.dead
                or (eaten_ghost[self.id] and powerup
                    and not returned_ghosts[self.id] and not self.dead)):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif (powerup and not self.dead
              and not eaten_ghost[self.id]
              and not returned_ghosts[self.id]):
            screen.blit(eatable_ghost, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead, (self.x_pos, self.y_pos))

        ghost_rect = pygame.Rect(
            (self.center_x - 18, self.center_y - 18),
            (36, 36)
        )
        return ghost_rect

    def check_collision(
        self,
        maze,
        offset_x: int,
        offset_y: int,
        ghost_size: tuple[int, int],
        ghost_speed: float,
        cell_size: int
    ):
        cell_x = (self.center_x - offset_x) // cell_size
        cell_y = (self.center_y - offset_y) // cell_size

        self.in_box = False

        if (cell_x, cell_y) not in maze.cells:
            self.turns = [False, False, False, False]
            return self.turns, self.in_box

        cell = maze.cells[(cell_x, cell_y)]

        # print(
        #         f"N={cell.North}, E={cell.East}, "
        #         f"S={cell.South}, W={cell.West}"
        #     )
        cell_center_x = offset_x + cell_x * cell_size + cell_size // 2
        cell_center_y = offset_y + cell_y * cell_size + cell_size // 2

        aligned_x = abs(self.center_x - cell_center_x) <= ghost_speed
        aligned_y = abs(self.center_y - cell_center_y) <= ghost_speed

        # print(
        #     f"aligned_x={aligned_x}, "
        #     f"aligned_y={aligned_y}"
        # )
        left_edge = offset_x + cell_x * cell_size
        right_edge = left_edge + cell_size
        top_edge = offset_y + cell_y * cell_size
        bottom_edge = top_edge + cell_size

        self.turns = [
            ((not cell.East or self.x_pos +
                ghost_size[0] + ghost_speed <= right_edge - 1)
                and aligned_y),
            ((not cell.West or self.x_pos - ghost_speed >= left_edge + 1)
                and aligned_y),
            ((not cell.North or self.y_pos - ghost_speed >= top_edge + 1)
                and aligned_x),
            ((not cell.South or self.y_pos + ghost_size[1] +
             ghost_speed <= bottom_edge - 1) and aligned_x),
        ]

        # print("offset:", offset_x, offset_y)
        # print("center:", self.center_x, self.center_y)
        # print("cell_size:", cell_size)
        # print(f"Ghost cell: ({cell_x}, {cell_y})")
        # print(f"Ghost position: ({self.x_pos}, {self.y_pos})")
        # print(f"Turns: {self.turns}")
        return self.turns, self.in_box

    def move(
                self,
                maze,
                offset_x: int,
                offset_y: int,
                cell_size: int
            ) -> tuple[int, int, int]:
        cell_x = (self.center_x - offset_x) // cell_size
        cell_y = (self.center_y - offset_y) // cell_size
        target_x = (self.target[0] - offset_x) // cell_size
        target_y = (self.target[1] - offset_y) // cell_size

        current_cell = (cell_x, cell_y)
        target_cell = (target_x, target_y)
        cell_center_x = offset_x + cell_x * cell_size + cell_size // 2
        cell_center_y = offset_y + cell_y * cell_size + cell_size // 2
        at_cell_center = (
            abs(self.center_x - cell_center_x) <= self.speed
            and abs(self.center_y - cell_center_y) <= self.speed
        )

        if (at_cell_center and
                current_cell in maze.cells and target_cell in maze.cells):
            directions = [
                (0, 1, 0, "East"),
                (1, -1, 0, "West"),
                (2, 0, -1, "North"),
                (3, 0, 1, "South"),
            ]
            queue: deque[tuple[int, int]] = deque([current_cell])

            previous: Dict[
                Tuple[int, int],
                Tuple[Optional[Tuple[int, int]], Optional[int]]
            ] = {current_cell: (None, None)}

            while queue and target_cell not in previous:
                current = queue.popleft()
                cell = maze.cells[current]
                for direction, dx, dy, wall in directions:
                    neighbor = (current[0] + dx, current[1] + dy)
                    if (getattr(cell, wall) or neighbor not in maze.cells
                            or maze.cells[neighbor].wall
                            or neighbor in previous):
                        continue
                    previous[neighbor] = (current, direction)
                    queue.append(neighbor)

            if target_cell in previous and target_cell != current_cell:
                next_cell = target_cell
                while previous[next_cell][0] != current_cell:
                    prev_node = previous[next_cell][0]
                    if prev_node is None:
                        break
                    next_cell = prev_node

                direction_val = previous[next_cell][1]
                if direction_val is not None:
                    self.direction = direction_val

        if self.direction == 0:
            self.x_pos = int(self.x_pos + self.speed)
        elif self.direction == 1:
            self.x_pos = int(self.x_pos - self.speed)
        elif self.direction == 2:
            self.y_pos = int(self.y_pos - self.speed)
        elif self.direction == 3:
            self.y_pos = int(self.y_pos + self.speed)

        self.center_x = self.x_pos + self.ghost_size[0] // 2
        self.center_y = self.y_pos + self.ghost_size[1] // 2

        return self.x_pos, self.y_pos, self.direction

    def align_ghost_to_cell(
        self,
        cell_size: int,
        offset_x: int,
        offset_y: int,
        ghost_size: tuple[int, int],
    ) -> tuple[int, int]:

        cell_x = (self.center_x - offset_x) // cell_size
        cell_y = (self.center_y - offset_y) // cell_size

        center_cell_x = offset_x + cell_x * cell_size + cell_size // 2
        center_cell_y = offset_y + cell_y * cell_size + cell_size // 2

        self.x_pos = center_cell_x - ghost_size[0] // 2
        self.y_pos = center_cell_y - ghost_size[1] // 2

        self.center_x = center_cell_x
        self.center_y = center_cell_y

        return self.x_pos, self.y_pos


def load_ghost_images(lev_num: int) -> list:
    ghost_images = []
    size = pacman_size(lev_num)

    red_img = pygame.image.load('assets/images/ghosts/red.png')
    red_img = pygame.transform.scale(red_img, size)
    ghost_images.append(red_img)

    blue_img = pygame.image.load('assets/images/ghosts/blue.png')
    blue_img = pygame.transform.scale(blue_img, size)
    ghost_images.append(blue_img)

    orange_img = pygame.image.load('assets/images/ghosts/orange.png')
    orange_img = pygame.transform.scale(orange_img, size)
    ghost_images.append(orange_img)

    pink_img = pygame.image.load('assets/images/ghosts/pink.png')
    pink_img = pygame.transform.scale(pink_img, size)
    ghost_images.append(pink_img)

    dead_img = pygame.image.load('assets/images/ghosts/dead.png')
    dead_img = pygame.transform.scale(dead_img, size)
    ghost_images.append(dead_img)

    powerup_img = pygame.image.load('assets/images/ghosts/powerup.png')
    powerup_img = pygame.transform.scale(powerup_img, size)
    ghost_images.append(powerup_img)

    return ghost_images


def ghost_position(lev_num: int, ghost: str) -> tuple[int, int]:
    if not (1 <= lev_num <= 10):
        raise ValueError("Invalid level")

    if ghost == "red":
        return (16, 16)
    elif ghost == "blue":
        return (848, 850)
    elif ghost == "pink":
        return (16, 850)
    elif ghost == "orange":
        return (848, 16)
    # print("Ghost position:", ghost.x, ghost.y)
    # print("Ghost cell:", (
    #     int((ghost.x + ghost.size//2 - offset_x) // cell_size),
    #     int((ghost.y + ghost.size//2 - offset_y) // cell_size)
    # ))
    raise ValueError(f"Unknown ghost: {ghost}")


def place_ghosts(
                    maze,
                    ghosts,
                    cell_size: int,
                    offset_x: int,
                    offset_y: int,
                    ghost_size: tuple[int, int]
                ) -> None:
    corners = [
        (0, 0),
        (maze.width - 1, maze.height - 1),
        (maze.width - 1, 0),
        (0, maze.height - 1),
    ]
    available_cells = [cell for cell in maze.cells.values() if not cell.wall]

    for ghost, corner in zip(ghosts, corners):
        cell = min(
            available_cells,
            key=lambda current_cell: (
                (abs(current_cell.x - corner[0]) +
                    abs(current_cell.y - corner[1])),
                current_cell.y,
                current_cell.x,
            ),
        )
        available_cells.remove(cell)
        ghost.x_pos = (offset_x + cell.x * cell_size +
                       cell_size // 2 - ghost_size[0] // 2)
        ghost.y_pos = (offset_y + cell.y * cell_size +
                       cell_size // 2 - ghost_size[1] // 2)
        ghost.center_x = ghost.x_pos + ghost_size[0] // 2
        ghost.center_y = ghost.y_pos + ghost_size[1] // 2
        ghost.start_x_pos = ghost.x_pos
        ghost.start_y_pos = ghost.y_pos

# def get_targets(
#     position_x: int,
#     position_y: int,
# ):
#     if position_x < 450:
#         runaway = 900
#     else:
#         runaway_x = 0
#         if position_x < 450:
#         runaway = 900
#     else:
#         runaway_x = 0
