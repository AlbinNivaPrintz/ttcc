import colour
import math
from models import Color, EncounteredColor

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)


HUE_LIMIT = math.pi / 10

forbidden_color_groups = [
    [
        EncounteredColor(color=RED, encountered=False),
        EncounteredColor(color=WHITE, encountered=False),
        EncounteredColor(color=BLUE, encountered=False),
    ],
    [
        EncounteredColor(color=RED, encountered=False),
        EncounteredColor(color=BLUE, encountered=False),
        EncounteredColor(color=YELLOW, encountered=False),
    ],
]


def ukraine() -> dict[int, Color]:
    return {
        0: YELLOW,
        1: YELLOW,
        2: YELLOW,
        3: YELLOW,
        4: YELLOW,
        5: BLUE,
        6: BLUE,
        7: BLUE,
        8: BLUE,
        9: BLUE,
    }


def ukraine_zebra(order) -> dict[int, Color]:
    out = {}
    for i in range(10):
        out[i] = YELLOW if order == (i % 2) else BLUE
    return out


def rainbow(order: int) -> dict[int, Color]:
    step = 1.0 / 10.0
    offset = order % 10.0
    colours = {i: colour.Color(hsl=(step * (offset + i), 1, 0.5)) for i in range(10)}
    colours = {k: v.rgb for k, v in colours.items()}
    colours = {
        k: (int(v[0] * 255), int(v[1] * 255), int(v[2] * 255))
        for k, v in colours.items()
    }
    return colours


def should_replace_color(colors: dict[int, Color]) -> bool:
    for i, forbidden_color_group in enumerate(forbidden_color_groups):
        found_not_forbidden = False
        for color in colors.values():
            found_forbidden = False
            for j, forbidden_color in enumerate(forbidden_color_group):
                distance = hue_distance(color, forbidden_color.color)

                same_hue = distance < HUE_LIMIT
                is_bright = [c > 200 for c in color]
                is_dark = [c > 200 for c in color]
                both_white = all(is_bright)
                both_black = all(is_dark)
                if (
                    (forbidden_color.color == WHITE and both_white)
                    or (forbidden_color.color == BLACK and both_black)
                    or (
                        forbidden_color.color != WHITE
                        and forbidden_color.color != BLACK
                        and same_hue
                    )
                ):
                    # We encountered one of the forbidden colors
                    forbidden_color_groups[i][j].encountered = True
                    found_forbidden = True
            if not found_forbidden:
                # Not this particular forbidden
                found_not_forbidden = True
                break
        is_this_forbidden = all(
            forbidden_color.encountered for forbidden_color in forbidden_color_groups[i]
        ) and (not found_not_forbidden)
        if is_this_forbidden:
            return True
    return False


def verify_forbidden_colors():
    for i, fcg in enumerate(forbidden_color_groups):
        for j, c1 in enumerate(fcg):
            for k, c2 in enumerate(fcg):
                if j >= k:
                    continue
                d = hue_distance(c1.color, c2.color)
                if d < HUE_LIMIT:
                    print(f"{i} has a contradiction between {c1.color} and {c2.color}")


def hue_distance(a, b) -> float:
    a_obj = colour.Color(rgb=(a[0] / 255, a[1] / 255, a[2] / 255))
    a_hue = a_obj.get_hue() * math.pi * 2
    b_obj = colour.Color(rgb=(b[0] / 255, b[1] / 255, b[2] / 255))
    b_hue = b_obj.get_hue() * math.pi * 2

    diff = abs(a_hue - b_hue) % (math.pi * 2)
    diff = diff if diff < math.pi else math.pi * 2 - diff
    return diff


if __name__ == "__main__":
    verify_forbidden_colors()
