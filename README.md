# Pac-Man — Ghosts! More ghosts!

## Description

This project is a playable Pac-Man-inspired arcade game written in Python
with Pygame. Guide Pac-Man through generated mazes, collect every pacgum,
use power pellets to make ghosts edible, and complete all ten levels before
running out of lives or time.

The game includes a graphical main menu, instructions, a top-player board,
level progression, configurable gameplay values, cheat controls for review,
and persistent score storage.

## Instructions

### Requirements

- Python 3.10 or newer
- [Pygame](https://www.pygame.org/docs/)

The A-Maze-ing generator used by the project is bundled under
`mazegenerator-00001/`; no separate installation is needed for it.

### Install and run

```bash
make install
make run
```

The Makefile also provides `make debug`, `make clean`, `make lint`, and
`make lint-strict`. On Linux, run `make package-linux` after `make install`
to create an itch.io-ready build in `dist/PacMan/`.

Use **New Game** in the menu, enter an alphanumeric player name of up to ten
characters, and start playing. For direct launch, pass the player name:

```bash
python3 pacman.py PlayerName
```

Run these commands from the repository root so the game can find `assets/`,
`config.json`, and the bundled maze generator.

### Controls

| Control | Action |
| --- | --- |
| Arrow keys | Move Pac-Man |
| `Ctrl` + `P` | Pause or resume |
| `Esc` | Open the pause menu |
| Up/Down + Enter | Choose Resume or Quit to Menu in the pause menu |
| `Ctrl` + `T` | Toggle invincibility |
| `Ctrl` + `W` | Complete the current level |
| `Ctrl` + `G` | Freeze or unfreeze ghosts |
| `Ctrl` + `L` | Add one life |
| `Ctrl` + `S` | Increase Pac-Man's speed |

The `Ctrl` shortcuts are cheat/review controls.

## Gameplay

- Eat regular pacgums to score 20 points each.
- Eat a power pellet (shown as a cherry) to score 50 points and make ghosts
  edible temporarily.
- Eat an edible ghost to score 200 points.
- Completing every regular pacgum advances to the next level.
- The game has ten levels. Lives and score carry between levels.
- Every level has a visible countdown. Time expiring ends the run.
- Contact with a non-edible ghost costs a life; Pac-Man then respawns in the
  maze.

## Configuration

The game reads [`config.json`](config.json) from the repository root. Its
top-level numbered keys (`"1"` through `"10"`) describe individual levels;
the remaining keys configure the game window and initial lives.

| Key | Default/current values | Purpose |
| --- | --- | --- |
| `width`, `height` | 14–22 cells | Maze dimensions for that level. |
| `ghosts` | 1–4 | Number of active ghosts. |
| `player_speed` | 2.0–3.0 | Pac-Man movement speed. |
| `ghost_speed` | 2.0–2.2 | Ghost movement speed. |
| `powerup_speed` | 1.7–3.2 | Reserved per-level power-up speed value. |
| `time_limit` | 120–180 seconds | Countdown duration for the level. |
| `window_width` | 900 | Game window width in pixels. |
| `window_height` | 960 | Game window height in pixels. |
| `wall_thickness` | 3 | Maze wall thickness in pixels. |
| `lives` | 3 | Lives at the start of a new game. |

Invalid level speeds, ghost counts, and time limits fall back to safe values
when the game starts. Keep all required keys and valid JSON syntax when
editing this file.

## Highscores

Scores are persisted in [`allResults.json`](allResults.json) as entries with
a player `name` and numeric `score`. A name is collected before a game starts;
the menu accepts only alphanumeric names with a maximum length of ten
characters. At the end of a won or lost game, the score is appended to this
file. The **Top Players** screen sorts saved entries in descending score order
and displays the ten highest entries.

Using JSON keeps scores portable, easy to inspect, and recoverable: a missing
or invalid score file is treated as an empty list rather than crashing the
menu. Returning to the menu with `Esc` does not save an in-progress score.

## Maze Generation

[`modifyMaze.py`](modifyMaze.py) loads the supplied A-Maze-ing package and
creates each level with `MazeGenerator`. It requests `perfect=False` to create
corridors appropriate for Pac-Man movement and uses the level number to select
a repeatable seed. The generated layout is adapted into the project's
`LevelMaze` and `Cell` objects, which store walls, pellets, and power-pellet
state. Four power pellets are placed at predefined corner-adjacent cells for
each level.

## Implementation

- Pygame renders the menu, maze, sprites, HUD, overlays, and input events.
- `pacman.py` owns the game loop: level setup, player/ghost updates, scoring,
  timer expiry, transitions, and game-end handling.
- Ghosts use breadth-first pathfinding to follow legal maze corridors toward
  their target or away from Pac-Man while frightened.
- Collision logic removes pacgums, handles power pellets, detects ghost
  encounters, and updates score/lives.

## General Software Architecture

```text
menu.py
  └─ launches pacman.py
       ├─ modifyMaze.py ──► bundled A-Maze-ing package
       ├─ player.py     ──► movement, sprite loading, wall checks
       ├─ ghost.py      ──► Ghost class, pathfinding, placement
       └─ scores.py     ──► scoring and allResults.json persistence
```

`config.json` supplies level and window settings to the game and maze module.
`assets/` contains the font and sprite images used by the menu and gameplay.

## Project Management

Project-management evidence should be kept in a dedicated
[`project_management/`](project_management/) directory, including planning,
task ownership, risks, progress tracking, and acceptance-test notes. Add the
team's documents there before submission.

## Resources

- [Pygame documentation](https://www.pygame.org/docs/)
- [Python documentation](https://docs.python.org/3/)
- [Pac-Man at The Arcade Museum](https://www.arcade-museum.com/Videogame/pac-man)
- Supplied **Pacman — Ghosts! More ghosts!** activity subject, Association 42,
  version 1.5.

### AI usage

OpenAI Codex was used to inspect the supplied subject, draft and refine this
README, and assist with small implementation changes (the level timer, HUD
placement, frightened-ghost wall collision guard, and Escape-to-menu control).
All generated changes were reviewed locally and checked with Python syntax and
configuration validation before use.
