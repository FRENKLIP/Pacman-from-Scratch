import pygame  # type: ignore[import-not-found]


player_images: list[pygame.Surface] = []
direction = 0
counter = 0
power_counter = 0
eaten_ghost = [False, False, False, False]
startup_counter = 0
movimg = False


def moving_pacman(running: bool):
    global counter
    global power_counter
    global eaten_ghost
    global startup_counter
    if counter < 19:
        counter += 1
    else:
        counter = 0
    if power_counter < 600:
        power_counter += 1
    elif power_counter >= 600:
        power_counter = 0
        eaten_ghost = [False, False, False, False]

    if startup_counter < 1:
        moving = False
        startup_counter += 1
    else:
        moving = True

    return counter, power_counter, eaten_ghost, moving


def pacman_size(lev_num: int) -> tuple[int, int]:
    if lev_num == 1 or lev_num == 2:
        height = 35
        width = 35
    elif lev_num == 3 or lev_num == 4:
        height = 32
        width = 32
    elif lev_num == 5 or lev_num == 6:
        height = 29
        width = 29
    elif lev_num == 7 or lev_num == 8:
        height = 26
        width = 26
    elif lev_num == 9 or lev_num == 10:
        height = 23
        width = 23
    return (height, width)


def load_player_images(lev_num: int) -> list:
    global player_images

    size = pacman_size(lev_num)

    player_images = []
    for i in range(1, 5):
        image = pygame.image.load(f"assets/images/player/{i}.png")
        image = pygame.transform.scale(image, size)
        player_images.append(image)
    return player_images


def level_middle_position(lev_num: int) -> tuple[int, int]:
    if lev_num == 1 or lev_num == 2:
        position_x = 400
        position_y = 400
    elif lev_num == 3 or lev_num == 4:
        position_x = 408
        position_y = 404
    elif lev_num == 5 or lev_num == 6:
        position_x = 408
        position_y = 400
    elif lev_num == 7 or lev_num == 8:
        position_x = 410
        position_y = 404
    elif lev_num == 9 or lev_num == 10:
        position_x = 416
        position_y = 414
    return (position_x, position_y)


def draw_player(
                    screen,
                    lev_num: int,
                    running: bool,
                    direction,
                    position_x: int,
                    position_y: int
                ) -> None:
    # 0-Right, 1-left, 2-up, 3-down
    counter = moving_pacman(running)[0]
    if direction == 0:
        screen.blit(
                        player_images[counter // 5],
                        (position_x, position_y)
                    )
    elif direction == 1:
        screen.blit(
                        pygame.transform.flip(
                                                player_images[counter // 5],
                                                True,
                                                False
                                            ),
                        (position_x, position_y)
                    )
    elif direction == 2:
        screen.blit(
                        pygame.transform.rotate(
                                                player_images[counter // 5],
                                                90
                                                ),
                        (position_x, position_y)
                    )
    elif direction == 3:
        screen.blit(
                        pygame.transform.rotate(
                                                player_images[counter // 5],
                                                270
                                                ),
                        (position_x, position_y)
                    )


def has_wall(maze, x: int, y: int, direction) -> bool:
    return getattr(maze.cells[(x, y)], direction)


def return_walls(maze, x: int, y: int) -> int:
    direction = 0
    if has_wall(maze, x, y, "West"):
        direction = 0
    elif has_wall(maze, x, y, "East"):
        direction = 1
    elif has_wall(maze, x, y, "South"):
        direction = 2
    elif has_wall(maze, x, y, "North"):
        direction = 3
    return direction


def find_cells(
                    player_x: int,
                    player_y: int,
                    cell_size: int,
                    offset_x: int,
                    offset_y: int,
                    player_size: tuple[int, int],
                ) -> tuple[int, int]:
    # Find which cell of the maze contains pac man
    center_x = player_x + player_size[0] // 2
    center_y = player_y + player_size[1] // 2
    cell_x = (center_x - offset_x) // cell_size
    cell_y = (center_y - offset_y) // cell_size
    return (cell_x, cell_y)


def check_position(
                        maze,
                        player_x: int,
                        player_y: int,
                        cell_size: int,
                        offset_x: int,
                        offset_y: int,
                        player_size: tuple[int, int],
                        player_speed: int
                    ) -> list:
    center_x = player_x + player_size[0] // 2
    center_y = player_y + player_size[1] // 2

    cell_x = (center_x - offset_x) // cell_size
    cell_y = (center_y - offset_y) // cell_size

    if (cell_x, cell_y) not in maze.cells:
        return [False, False, False, False]

    cell = maze.cells[(cell_x, cell_y)]

    cell_center_x = offset_x + cell_x * cell_size + cell_size // 2
    cell_center_y = offset_y + cell_y * cell_size + cell_size // 2

    aligned_x = abs(center_x - cell_center_x) <= player_speed
    aligned_y = abs(center_y - cell_center_y) <= player_speed

    left_edge = offset_x + cell_x * cell_size
    right_edge = left_edge + cell_size
    top_edge = offset_y + cell_y * cell_size
    bottom_edge = top_edge + cell_size

    return [
        ((not cell.East or player_x + player_size[0] +
            player_speed <= right_edge - 1) and aligned_y),
        ((not cell.West or player_x -
            player_speed >= left_edge + 1) and aligned_y),
        ((not cell.North or player_y -
            player_speed >= top_edge + 1) and aligned_x),
        ((not cell.South or player_y + player_size[1] +
            player_speed <= bottom_edge - 1) and aligned_x),
    ]


def check_turns(
                    maze,
                    player_x: int,
                    player_y: int,
                    cell_size: int,
                    offset_x: int,
                    offset_y: int,
                    player_size: tuple[int, int],
                    player_speed: int
                ) -> list:
    center_x = player_x + player_size[0] // 2
    center_y = player_y + player_size[1] // 2

    cell_x = (center_x - offset_x) // cell_size
    cell_y = (center_y - offset_y) // cell_size

    if (cell_x, cell_y) not in maze.cells:
        return [False, False, False, False]

    cell = maze.cells[(cell_x, cell_y)]

    cell_center_x = offset_x + cell_x * cell_size + cell_size // 2
    cell_center_y = offset_y + cell_y * cell_size + cell_size // 2

    aligned_x = abs(center_x - cell_center_x) <= player_speed
    aligned_y = abs(center_y - cell_center_y) <= player_speed
    return [
        not cell.East and aligned_y,
        not cell.West and aligned_y,
        not cell.North and aligned_x,
        not cell.South and aligned_x,
    ]


def align_player_to_cell(
                            player_x: int,
                            player_y: int,
                            direction: int,
                            cell_size: int,
                            offset_x: int,
                            offset_y: int,
                            player_size: tuple[int, int]
                        ) -> tuple[int, int]:
    center_x = player_x + player_size[0] // 2
    center_y = player_y + player_size[1] // 2
    cell_x = (center_x - offset_x) // cell_size
    cell_y = (center_y - offset_y) // cell_size

    if direction in (0, 1):
        player_y = (offset_y + cell_y * cell_size +
                    cell_size // 2 - player_size[1] // 2)
    else:
        player_x = (offset_x + cell_x * cell_size +
                    cell_size // 2 - player_size[0] // 2)
    return (player_x, player_y)


def move_player(
                    pos_x: int,
                    pos_y: int,
                    direction: int,
                    turns_allowed: list,
                    player_speed: float
                ) -> tuple[int, int]:
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        pos_x = int(pos_x + player_speed)
    elif direction == 1 and turns_allowed[1]:
        pos_x = int(pos_x - player_speed)
    elif direction == 2 and turns_allowed[2]:
        pos_y = int(pos_y - player_speed)
    elif direction == 3 and turns_allowed[3]:
        pos_y = int(pos_y + player_speed)
    return (pos_x, pos_y)
