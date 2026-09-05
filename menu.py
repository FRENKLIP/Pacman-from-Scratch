import json
import pygame  # type: ignore[import-not-found]
import sys
import subprocess

pygame.init()

# Window Configuration
WIDTH = 900
HEIGHT = 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac - Man")

BACKGROUND_COLOR = (101, 81, 129)
background = pygame.Surface((WIDTH, HEIGHT))
background.fill(BACKGROUND_COLOR)

YELLOW = (252, 191, 73)
TRANSLUCENT_PURPLE = (179, 136, 235, 180)
HOVER_BLUE = (0, 140, 255, 220)
SHADOW = (0, 0, 0)

# Fonts
try:
    FONT_TITLE = pygame.font.Font("assets/font/font.ttf", 72)
    FONT_BUTTON = pygame.font.Font("assets/font/font.ttf", 36)
    FONT_TEXT = pygame.font.Font("assets/font/font.ttf", 28)
    FONT_MESSAGE = pygame.font.Font("assets/font/font.ttf", 20)
except (FileNotFoundError, OSError):
    FONT_TITLE = pygame.font.SysFont(None, 72)
    FONT_BUTTON = pygame.font.SysFont(None, 36)
    FONT_TEXT = pygame.font.SysFont(None, 28)


class Button:
    def __init__(self, text, center_y, action):
        self.text = text
        self.center_y = center_y
        self.action = action
        self.width, self.height = 440, 70
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (WIDTH // 2, center_y)

    def draw(self, win, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = HOVER_BLUE if is_hovered else TRANSLUCENT_PURPLE

        button_surface = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            button_surface, color, (0, 0, self.width, self.height),
            border_radius=16
        )
        win.blit(button_surface, self.rect)

        text_surf = FONT_BUTTON.render(self.text, True, YELLOW)
        text_rect = text_surf.get_rect(center=self.rect.center)

        shadow = FONT_BUTTON.render(self.text, True, SHADOW)
        win.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
        win.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


buttons = [
    Button("New Game", 350, "new"),
    Button("Top Players", 430, "options"),
    Button("Quit", 510, "quit")
]


def load_top_players():
    try:
        with open("allResults.json", "r") as file:
            result = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        result = []

    if isinstance(result, dict):
        scores_list = result.get("scores", [])
    elif isinstance(result, list):
        scores_list = result
    else:
        scores_list = []

    formatted_scores = []
    for item in scores_list:
        if isinstance(item, dict):
            name = item.get("name", "Unknown")
            score = item.get("score", 0)
            formatted_scores.append({"name": name, "score": score})
        else:
            formatted_scores.append({"name": "Player", "score": item})

    sorted_players = sorted(
        formatted_scores,
        key=lambda x: x["score"],
        reverse=True
        )
    return sorted_players[:3]


def show_top_players_screen():
    clock = pygame.time.Clock()
    top_players = load_top_players()

    back_button = Button("Back", 750, "back")

    while True:
        clock.tick(60)
        screen.blit(background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = FONT_TITLE.render("Top Players", True, YELLOW)
        shadow = FONT_TITLE.render("Top Players", True, SHADOW)
        screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 103))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        start_y = 350
        if not top_players:
            no_data_surf = FONT_TEXT.render(
                "No scores recorded yet!",
                True,
                YELLOW
                )
            screen.blit(
                no_data_surf,
                (WIDTH // 2 - no_data_surf.get_width() // 2, start_y)
                )
        else:
            for i, player in enumerate(top_players):
                name = player.get("name", "Unknown")
                score = player.get("score", 0)

                player_text = f"{i + 1}.{name} -> {score}"

                font = FONT_TEXT

                while font.size(player_text)[0] > WIDTH - 100:
                    font = pygame.font.Font(
                        "assets/font/font.ttf",
                        font.get_height() - 1
                    )

                text_surf = font.render(player_text, True, YELLOW)
                shadow_surf = font.render(player_text, True, SHADOW)

                text_rect = text_surf.get_rect(
                    center=(WIDTH // 2, start_y + (i * 80))
                )
                screen.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
                screen.blit(text_surf, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.is_clicked(event.pos):
                    pygame.time.delay(100)
                    return

        back_button.draw(screen, mouse_pos)
        pygame.display.flip()


def is_repeated(u_name: str) -> bool: 
    try:
        with open("allResults.json", "r") as file:
            all_results = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return False


    for player in all_results:
        if player["name"] == u_name:
            return True

    return False


def get_uname() -> str:
    clock = pygame.time.Clock()
    uname = ""
    active = True
    back_button = Button("Back", 750, "back")
    input_rect = pygame.Rect( WIDTH // 2 - 220, 320, 440, 70 )
    input_color = (80, 80, 120)
    input_border = YELLOW
    repeated = False

    while active:
        mouse_pos = pygame.mouse.get_pos()
        clock.tick(60)
        screen.blit(background, (0,0))

        title = FONT_TITLE.render("Write Username", True, YELLOW)
        shadow = FONT_TITLE.render("Write Username", True, YELLOW)

        screen.blit(
            shadow,
            (WIDTH // 2 - title.get_width() // 2 + 3, 103)
        )
        screen.blit(
            title,
            (WIDTH // 2 - title.get_width()// 2, 100)
        )

        pygame.draw.rect(
            screen,
            input_color,
            input_rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            input_border,
            input_rect,
            width=3,
            border_radius=12
        )

        uname_surf = FONT_TEXT.render(uname, True, YELLOW)
        uname_rect = uname_surf.get_rect(center = (WIDTH // 2, 350))

        screen.blit(uname_surf, uname_rect)

        if repeated:
            text = FONT_MESSAGE.render(
                    "This username already exist. Please write another one.",
                    True,
                    (0,0,0)
                )
            text_rect = text.get_rect(center=(WIDTH // 2, 420))
            screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    if is_repeated(uname):
                        repeated = True
                    else:
                        return uname.strip()

                elif event.key == pygame.K_BACKSPACE:
                    uname = uname[:-1]
                    repeated = False

                else:
                    if len(uname) < 15:
                        uname += event.unicode
                        repeated = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.is_clicked(event.pos):
                    pygame.time.delay(100)
                    return ""

        back_button.draw(screen, mouse_pos)
        pygame.display.flip()
    return uname


def handle_action(action):
    if action == "new":
        uname = get_uname()

        # Back was pressed
        if not uname:
            return True

        pygame.quit()
        subprocess.run(
            [sys.executable, "pacman.py", uname]
        )
        sys.exit()

    elif action == "options":
        show_top_players_screen()

    elif action == "quit":
        return False

    return True



def show_menu():
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        screen.blit(background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = FONT_TITLE.render("Pac - Man", True, YELLOW)
        shadow = FONT_TITLE.render("Pac - Man", True, SHADOW)
        screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 103))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn.is_clicked(event.pos):
                        pygame.time.delay(100)
                        running = handle_action(btn.action)

        for btn in buttons:
            btn.draw(screen, mouse_pos)

        pygame.display.flip()

    pygame.quit()
    print("Game closed")


if __name__ == "__main__":
    show_menu()
