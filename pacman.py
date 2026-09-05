import pygame  # type: ignore[import-not-found]
import json
import sys
import ghost as ghost_module
from modifyMaze import create_level_maze
from player import (
                    draw_player,
                    load_player_images,
                    check_position,
                    check_turns,
                    align_player_to_cell,
                    move_player,
                    pacman_size,
                    find_cells,
                    moving_pacman
                    )
from scores import check_collision, save_scores, points_ghost
from ghost import (
    Ghost,
    load_ghost_images,
    red_dead,
    blue_dead,
    orange_dead,
    pink_dead,
    red_box,
    blue_box,
    orange_box,
    pink_box,
    place_ghosts
)

with open("config.json", "r") as file:
    config = json.load(file)

WINDOW_SIZE = config["window_width"]
WINDOW_HEIGHT = config["window_height"]
WINDOW_WIDTH = config["window_width"]
# Keep the gameplay screen visually consistent with menu.py.
MENU_YELLOW = (252, 191, 73)
MENU_PURPLE = (179, 136, 235)
MENU_SHADOW = (0, 0, 0)
BACKGROUND_COLOR = (101, 81, 129)
MAZE_BLOCK_COLOR = (96, 72, 133)
WALL_COLOR = MENU_YELLOW
PELLET_COLOR = MENU_YELLOW
PATTERN_BACKGROUND_COLOR = MAZE_BLOCK_COLOR
WALL_THICKNESS = config["wall_thickness"]
LEVEL_NUMBER = 1

turns_allowed = [False, False, False, False]
# Right, lrft, up, down

direction_command = 0

scores = 0
powerup = False
power_counter = 0
eaten_ghosts = [False, False, False, False]
returned_ghosts = [False, False, False, False]
moving = False
lives = config["lives"]

red_direction = 0
blue_direction = 0
orange_direction = 0
pink_direction = 0
dead = False


def draw_line(
                screen,
                start: tuple[int, int],
                end: tuple[int, int]
            ) -> None:
    screen_width, screen_height = screen.get_size()
    start = (min(start[0], screen_width - 1), min(start[1], screen_height - 1))
    end = (min(end[0], screen_width - 1), min(end[1], screen_height - 1))
    pygame.draw.line(screen, WALL_COLOR, start, end, WALL_THICKNESS)


def draw_maze(
                screen,
                maze,
                cell_size: int,
                offset_x: int,
                offset_y: int
            ) -> None:
    for cell in maze.cells.values():
        x = offset_x + cell.x * cell_size
        y = offset_y + cell.y * cell_size

        if cell.wall:
            pygame.draw.rect(
                screen,
                PATTERN_BACKGROUND_COLOR,
                (x, y, cell_size, cell_size)
            )
            for direction, neighbor in maze.get_neighbors(cell.x, cell.y):
                if not neighbor.wall:
                    if direction == "North":
                        draw_line(
                            screen,
                            (x, y),
                            (x + cell_size, y)
                        )
                    elif direction == "East":
                        draw_line(
                            screen,
                            (x + cell_size, y),
                            (x + cell_size, y + cell_size)
                        )
                    elif direction == "South":
                        draw_line(
                            screen,
                            (x, y + cell_size),
                            (x + cell_size, y + cell_size)
                        )
                    else:
                        draw_line(
                            screen,
                            (x, y),
                            (x, y + cell_size)
                        )
            continue

        if cell.North:
            draw_line(
                screen,
                (x, y),
                (x + cell_size, y)
            )
        if cell.East:
            draw_line(
                screen,
                (x + cell_size, y),
                (x + cell_size, y + cell_size)
            )
        if cell.South:
            draw_line(
                screen,
                (x, y + cell_size),
                (x + cell_size, y + cell_size)
            )
        if cell.West:
            draw_line(
                screen,
                (x, y),
                (x, y + cell_size)
            )


def draw_pellets(
                    screen,
                    maze,
                    cell_size: int,
                    offset_x: int,
                    offset_y: int,
                    pellet_image,
                    cherry_image
                ) -> int:
    pacgum = 0
    img_width, img_height = pellet_image.get_size()

    for cell in maze.cells.values():
        if cell.power_pellet:
            x = offset_x + cell.x * cell_size + cell_size // 2
            y = offset_y + cell.y * cell_size + cell_size // 2

            screen.blit(
                cherry_image,
                (x - cherry_image.get_width() // 2,
                y - cherry_image.get_height() // 2)
            )

        elif cell.pellet:
            x = offset_x + cell.x * cell_size + cell_size // 2
            y = offset_y + cell.y * cell_size + cell_size // 2

            screen.blit(
                pellet_image,
                (x - pellet_image.get_width() // 2,
                y - pellet_image.get_height() // 2)
            )
            pacgum += 1
    return pacgum


def start_position(
                        maze,
                        cellSize: int,
                        offset_x: int,
                        offset_y: int,
                        player_size: list
                    ) -> tuple[int, int]:
    middle_x = (maze.width - 1) / 2
    middle_y = (maze.height - 1) / 2
    cell = min(
        (cell for cell in maze.cells.values() if not cell.wall),
        key=lambda cell: (
            abs(cell.x - middle_x) + abs(cell.y - middle_y),
            cell.y,
            cell.x
        ),
    )
    pos_x = offset_x + cell.x * cellSize + cellSize // 2 - player_size[0] // 2
    pos_y = offset_y + cell.y * cellSize + cellSize // 2 - player_size[1] // 2
    return pos_x, pos_y


def target_at_cell(
                    maze,
                    cell_x: int,
                    cell_y: int,
                    cell_size: int,
                    offset_x: int,
                    offset_y: int,
                ) -> tuple[int, int]:
    """Return the center of the closest walkable cell to a desired cell."""
    cell_x = max(0, min(cell_x, maze.width - 1))
    cell_y = max(0, min(cell_y, maze.height - 1))
    target_cell = min(
        (cell for cell in maze.cells.values() if not cell.wall),
        key=lambda cell: (
            abs(cell.x - cell_x) + abs(cell.y - cell_y),
            cell.y,
            cell.x,
        ),
    )
    return (
        offset_x + target_cell.x * cell_size + cell_size // 2,
        offset_y + target_cell.y * cell_size + cell_size // 2,
    )


def frightened_target(
                    maze,
                    player_target: tuple[int, int],
                    ghost_id: int,
                    cell_size: int,
                    offset_x: int,
                    offset_y: int,
                ) -> tuple[int, int]:
    """Choose a distant walkable cell while a ghost is frightened."""
    player_x = (player_target[0] - offset_x) // cell_size
    player_y = (player_target[1] - offset_y) // cell_size
    walkable = [cell for cell in maze.cells.values() if not cell.wall]
    # Keep ghosts from all selecting exactly the same escape destination.
    candidates = sorted(
        walkable,
        key=lambda cell: (
            abs(cell.x - player_x) + abs(cell.y - player_y),
            cell.y,
            cell.x,
        ),
        reverse=True,
    )
    target_cell = candidates[min(ghost_id * 8, len(candidates) - 1)]
    return (
        offset_x + target_cell.x * cell_size + cell_size // 2,
        offset_y + target_cell.y * cell_size + cell_size // 2,
    )


def player_ahead_target(
                        maze,
                        position_x: int,
                        position_y: int,
                        direction: int,
                        tiles_ahead: int,
                        cell_size: int,
                        offset_x: int,
                        offset_y: int,
                        player_size: tuple[int, int],
                    ) -> tuple[int, int]:
    """Find the furthest reachable cell straight ahead of Pac-Man."""
    cell_x, cell_y = find_cells(
        position_x,
        position_y,
        cell_size,
        offset_x,
        offset_y,
        player_size,
    )
    steps = {
        0: (1, 0, "East"),
        1: (-1, 0, "West"),
        2: (0, -1, "North"),
        3: (0, 1, "South"),
    }
    delta_x, delta_y, wall = steps[direction]

    for _ in range(tiles_ahead):
        current = maze.cells[(cell_x, cell_y)]
        next_cell = (cell_x + delta_x, cell_y + delta_y)
        if (getattr(current, wall) or next_cell not in maze.cells
                or maze.cells[next_cell].wall):
            break
        cell_x, cell_y = next_cell

    return target_at_cell(
        maze, cell_x, cell_y, cell_size, offset_x, offset_y
    )


def draw_misc(screen):
    try:
        font = pygame.font.Font("assets/font/font.ttf", 28)
        label_font = pygame.font.Font("assets/font/font.ttf", 20)
    except (FileNotFoundError, OSError):
        font = pygame.font.SysFont(None, 28)
        label_font = pygame.font.SysFont(None, 20)

    hud_rect = pygame.Rect(14, WINDOW_SIZE + 8, WINDOW_WIDTH - 28, 44)
    hud_surface = pygame.Surface(hud_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(
        hud_surface,
        (*MENU_PURPLE, 210),
        hud_surface.get_rect(),
        border_radius=12,
    )
    screen.blit(hud_surface, hud_rect)

    score_text = font.render(f'Score: {scores}', True, MENU_YELLOW)
    score_shadow = font.render(f'Score: {scores}', True, MENU_SHADOW)
    screen.blit(score_shadow, (28, WINDOW_SIZE + 18))
    screen.blit(score_text, (26, WINDOW_SIZE + 16))

    level_text = label_font.render(f'Level {LEVEL_NUMBER}', True, MENU_YELLOW)
    level_shadow = label_font.render(f'Level {LEVEL_NUMBER}', True, MENU_SHADOW)
    level_pos = (WINDOW_WIDTH // 2 - level_text.get_width() // 2,
                 WINDOW_SIZE + 21)
    screen.blit(level_shadow, (level_pos[0] + 2, level_pos[1] + 2))
    screen.blit(level_text, level_pos)

    lives_text = label_font.render('Lives', True, MENU_YELLOW)
    lives_shadow = label_font.render('Lives', True, MENU_SHADOW)
    screen.blit(lives_shadow, (WINDOW_WIDTH - 214, WINDOW_SIZE + 22))
    screen.blit(lives_text, (WINDOW_WIDTH - 216, WINDOW_SIZE + 20))
    player_images = load_player_images(LEVEL_NUMBER)

    if powerup:
        pygame.draw.circle(screen, MENU_YELLOW, (205, WINDOW_SIZE + 30), 12)
    for i in range(lives):
        image = pygame.transform.scale(
            player_images[0],
            (26, 26)
        )
        screen.blit(
            image,
            (WINDOW_WIDTH - 150 + i * 34, WINDOW_SIZE + 17)
        )


def main(u_name: str) -> None:
    global scores
    global power_counter
    global powerup
    global eaten_ghosts
    global returned_ghosts
    global red_direction
    global LEVEL_NUMBER
    global lives

    playerSpeed = config[str(LEVEL_NUMBER)]["player_speed"]
    ghostSpeed = config[str(LEVEL_NUMBER)]["ghost_speed"]

    pygame.init()
    load_player_images(LEVEL_NUMBER)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(
        f"Pac-Man - Level {LEVEL_NUMBER}"
    )
    clock = pygame.time.Clock()

    level_background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    level_background.fill(BACKGROUND_COLOR)

    maze = create_level_maze(LEVEL_NUMBER)

    cell_size = min(WINDOW_WIDTH // maze.width, WINDOW_SIZE // maze.height)
    offset_x = (WINDOW_SIZE - maze.width * cell_size) // 2
    offset_y = (WINDOW_SIZE - maze.height * cell_size) // 2

    pellet_size = max(25, cell_size // 25)
    PELLET_IMAGE = pygame.image.load('assets/images/pokeball.png')
    PELLET_IMAGE.convert_alpha()
    PELLET_IMAGE = pygame.transform.scale(
        PELLET_IMAGE, (pellet_size, pellet_size)
        )
    CHERRY_IMAGE = pygame.image.load("assets/images/cherry.png")
    CHERRY_IMAGE = pygame.transform.scale(
      CHERRY_IMAGE, (pellet_size, pellet_size)
  )


    player_size = pacman_size(LEVEL_NUMBER)
    ghost_size = pacman_size(LEVEL_NUMBER)
    position_x, position_y = start_position(
        maze,
        cell_size,
        offset_x,
        offset_y,
        player_size
    )

    cell_x, cell_y = find_cells(
        position_x,
        position_y,
        cell_size,
        offset_x,
        offset_y,
        player_size
    )

    turns_allowed = check_position(
        maze,
        position_x,
        position_y,
        cell_size,
        offset_x,
        offset_y,
        player_size,
        playerSpeed
    )

    turns_to_turn = check_turns(
        maze,
        position_x,
        position_y,
        cell_size,
        offset_x,
        offset_y,
        player_size,
        playerSpeed
    )
    direction = next(
        index for index, allowed in enumerate(turns_to_turn) if allowed
    )
    direction_command = direction

    targets = [
        (position_x, position_y),
        (position_x, position_y),
        (position_x, position_y),
        (position_x, position_y)
        ]
    # red, blue, orange, pink, dead, powerup
    ghost_images = load_ghost_images(LEVEL_NUMBER)
    ghost_module.eatable_ghost = ghost_images[5]

    red_ghost = Ghost(
        targets[0],
        ghostSpeed,
        ghost_images[0],
        red_direction,
        red_dead,
        red_box,
        0,
        LEVEL_NUMBER,
        "red",
        screen,
        maze,
        offset_x,
        offset_y,
        ghost_size,
        cell_size,
        eaten_ghosts
    )

    blue_ghost = Ghost(
        targets[1],
        ghostSpeed,
        ghost_images[1],
        blue_direction,
        blue_dead,
        blue_box,
        1,
        LEVEL_NUMBER,
        "blue",
        screen,
        maze,
        offset_x,
        offset_y,
        ghost_size,
        cell_size,
        eaten_ghosts
    )

    orange_ghost = Ghost(
        targets[2],
        ghostSpeed,
        ghost_images[2],
        orange_direction,
        orange_dead,
        orange_box,
        2,
        LEVEL_NUMBER,
        "orange",
        screen,
        maze,
        offset_x,
        offset_y,
        ghost_size,
        cell_size,
        eaten_ghosts
    )

    pink_ghost = Ghost(
        targets[3],
        ghostSpeed,
        ghost_images[3],
        pink_direction,
        pink_dead,
        pink_box,
        3,
        LEVEL_NUMBER,
        "pink",
        screen,
        maze,
        offset_x,
        offset_y,
        ghost_size,
        cell_size,
        eaten_ghosts
    )

    # Keep the four ghost definitions available for their targeting logic,
    # but only activate the number configured for this level.
    all_ghosts = [red_ghost, blue_ghost, orange_ghost, pink_ghost]
    ghost_count = config[str(LEVEL_NUMBER)]["ghosts"]
    ghosts = all_ghosts[:ghost_count]
    place_ghosts(
        maze,
        ghosts,
        cell_size,
        offset_x,
        offset_y,
        ghost_size,
    )

    running = True
    # pacman_has_moved = False
    while running:
        if powerup:
            power_counter += 1

        if power_counter >= 600:
            powerup = False
            power_counter = 0
            eaten_ghosts = [False, False, False, False]
            returned_ghosts = [False, False, False, False]
        ghost_module.powerup = powerup
        ghost_module.returned_ghosts = returned_ghosts


        pygame.display.set_caption(
                f"Pac-Man - Level {LEVEL_NUMBER}"
            )
        screen.blit(level_background, (0, 0))

        pacgum = draw_pellets(
            screen,
            maze,
            cell_size,
            offset_x,
            offset_y,
            PELLET_IMAGE,
            CHERRY_IMAGE
        )
        draw_maze(screen, maze, cell_size, offset_x, offset_y)
        draw_misc(screen)
        draw_player(
            screen,
            LEVEL_NUMBER,
            running,
            direction,
            position_x,
            position_y
        )
        for ghost in ghosts:
            ghost.draw(screen, eaten_ghosts, dead)
        # center_x = position_x + 18
        # center_y = position_y + 18
        # pygame.draw.circle(screen, 'white', (center_x, center_y), 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    direction_command = 0
                elif event.key == pygame.K_LEFT:
                    direction_command = 1
                elif event.key == pygame.K_UP:
                    direction_command = 2
                elif event.key == pygame.K_DOWN:
                    direction_command = 3

        turns_allowed = check_position(
            maze,
            position_x,
            position_y,
            cell_size,
            offset_x,
            offset_y,
            player_size,
            playerSpeed
        )

        turns_to_turn = check_turns(
            maze,
            position_x,
            position_y,
            cell_size,
            offset_x,
            offset_y,
            player_size,
            playerSpeed
        )

        cell_x, cell_y = find_cells(
            position_x,
            position_y,
            cell_size,
            offset_x,
            offset_y,
            player_size,
        )
        cell = maze.cells[(cell_x, cell_y)]

        requested_direction_open = [
            not cell.East,   # right
            not cell.West,   # left
            not cell.North,  # up
            not cell.South,  # down
        ][direction_command]


        if turns_to_turn[direction_command]:
            position_x, position_y = align_player_to_cell(
                position_x,
                position_y,
                direction_command,
                cell_size,
                offset_x,
                offset_y,
                player_size,
            )
            direction = direction_command

        elif not turns_allowed[direction] and requested_direction_open:
            position_x, position_y = align_player_to_cell(
                position_x,
                position_y,
                direction_command,
                cell_size,
                offset_x,
                offset_y,
                player_size,
            )
            direction = direction_command

        turns_allowed = check_position(
            maze,
            position_x,
            position_y,
            cell_size,
            offset_x,
            offset_y,
            player_size,
            playerSpeed
        )

        moving = moving_pacman(running)[3]
        if moving:
            # previous_position = (position_x, position_y)
            position_x, position_y = move_player(
                position_x,
                position_y,
                direction,
                turns_allowed,
                playerSpeed
            )

            # if (position_x, position_y) != previous_position:
            #     pacman_has_moved = True

        player_target = (
            position_x + player_size[0] // 2,
            position_y + player_size[1] // 2,
        )
        pink_target = player_ahead_target(
            maze,
            position_x,
            position_y,
            direction,
            4,
            cell_size,
            offset_x,
            offset_y,
            player_size,
        )
        inky_reference = player_ahead_target(
            maze,
            position_x,
            position_y,
            direction,
            2,
            cell_size,
            offset_x,
            offset_y,
            player_size,
        )
        blue_target = target_at_cell(
            maze,
            ((2 * inky_reference[0] - red_ghost.center_x - offset_x)
             // cell_size),
            ((2 * inky_reference[1] - red_ghost.center_y - offset_y)
             // cell_size),
            cell_size,
            offset_x,
            offset_y,
        )
        orange_distance = ((orange_ghost.center_x - player_target[0]) ** 2 +
                           (orange_ghost.center_y - player_target[1]) ** 2)
        orange_target = (
            player_target if orange_distance > (8 * cell_size) ** 2
            else target_at_cell(
                maze,
                0,
                maze.height - 1,
                cell_size,
                offset_x,
                offset_y,
            )
        )

        normal_targets = [player_target, blue_target, orange_target, pink_target]
        for ghost, normal_target in zip(ghosts, normal_targets):
            target = (
                frightened_target(
                    maze,
                    player_target,
                    ghost.id,
                    cell_size,
                    offset_x,
                    offset_y,
                )
                if powerup and not eaten_ghosts[ghost.id]
                else normal_target
            )
            ghost.target = target
            ghost.turns, ghost.in_box = ghost.check_collision(
                maze,
                offset_x,
                offset_y,
                ghost_size,
                ghostSpeed,
                cell_size,
            )
            ghost.move(
                maze,
                offset_x,
                offset_y,
                cell_size,
            )

        cell_x, cell_y = find_cells(
                                        position_x,
                                        position_y,
                                        cell_size,
                                        offset_x,
                                        offset_y,
                                        player_size
                                    )
        pellet = maze.cells[(cell_x, cell_y)].pellet

        center_x = position_x + player_size[0] // 2
        center_y = position_y + player_size[1] // 2

        cell = maze.cells[(cell_x, cell_y)]
        cherry_x = offset_x + cell_x * cell_size + cell_size // 2
        cherry_y = offset_y + cell_y * cell_size + cell_size // 2

        if (
            cell.power_pellet
            and abs(center_x - cherry_x) <= 3
            and abs(center_y - cherry_y) <= 3
        ):
            cell.power_pellet = False
            powerup = True
            power_counter = 0
            scores += 50
            ghost_module.powerup = True


        pacman_rec = pygame.Rect(position_x,position_y,player_size[0],player_size[1])
        for x in ghosts:
            if pacman_rec.colliderect(pygame.Rect(x.x_pos , x.y_pos , ghost_size[0] , ghost_size[1])):
                if powerup and not eaten_ghosts[x.id]:
                    scores += points_ghost
                    eaten_ghosts[x.id] = True
                    x.reset_position()
                    returned_ghosts[x.id] = True
                    continue

                lives -= 1
                if lives > 0:
                    position_x, position_y = start_position(
                        maze,
                        cell_size,
                        offset_x,
                        offset_y,
                        player_size
                    )
                    place_ghosts(
                        maze,
                        ghosts,
                        cell_size,
                        offset_x,
                        offset_y,
                        ghost_size,
                    )
                else:
                    running = False
                break
                    

        scores, power_count, eaten_ghosts = check_collision(
            maze,
            scores,
            "pacgum",
            pellet,
            cell_x,
            cell_y,
            center_x,
            center_y,
            cell_size,
            offset_x,
            offset_y,
            power_counter,
            eaten_ghosts
        )
        # print("Current direction:", direction)
        # print("Wanted direction:", direction_command)

        if position_x > WINDOW_SIZE:
            position_x = -47
        elif position_x < -50:
            position_x = 897

        if pacgum == 0 and LEVEL_NUMBER < 10:
            LEVEL_NUMBER += 1
            main(u_name)
        elif pacgum == 0 and LEVEL_NUMBER == 10:
            break

        pygame.display.flip()
        clock.tick(60) 

    save_scores(scores, u_name)
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        u_name = sys.argv[1]
    else:
        u_name = "Player"

    main(u_name)
