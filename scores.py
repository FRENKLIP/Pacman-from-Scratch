import json

score = 0
points_pacgum = 20
points_super_pacgum = 50
points_ghost = 200

# def draw_superPacgum() -> None:


def check_collision(
        maze,
        scores: int,
        eaten_object: str,
        pellet: bool,
        cell_x: int,
        cell_y: int,
        center_x: int,
        center_y: int,
        cell_size: int,
        offset_x: int,
        offset_y: int,
        power_count: int,
        eaten_ghost: list
        ) -> tuple[int, int, list]:
    # Centre of the cell where the pacgum is
    pellet_x = offset_x + cell_x * cell_size + cell_size // 2
    pellet_y = offset_y + cell_y * cell_size + cell_size // 2

    if abs(center_x - pellet_x) <= 3 and abs(center_y - pellet_y) <= 3:
        if pellet:
            if eaten_object == "pacgum":
                scores += points_pacgum
                maze.cells[(cell_x, cell_y)].pellet = False
            elif eaten_object == "superPacgum":
                scores += points_super_pacgum
            elif eaten_object == "ghost":
                scores += points_ghost
                # power = True
                power_count = 0
                eaten_ghost = [False, False, False, False]
    return scores, power_count, eaten_ghost


def save_scores(scores, u_name):
    try:
        with open("allResults.json", "r") as file:
            result = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        result = []

    new_entry = {"name": u_name, "score": scores}
    result.append(new_entry)

    with open("allResults.json", "w") as file:
        json.dump(result, file, indent=4)


def find_top_players():
    try:
        with open("allResults.json", "r") as file:
            result = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        result = {"scores": []}

    sorted_players = sorted(
        result["scores"],
        key=lambda x: x["score"], reverse=True
        )

    top_3 = sorted_players[:3]

    for player in top_3:
        print(f"Name: {player['name']}, Score: {player['score']}")

    return top_3
