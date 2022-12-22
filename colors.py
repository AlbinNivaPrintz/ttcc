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
    # Russia
    [
        EncounteredColor(color=WHITE, encountered=False),
        EncounteredColor(color=BLUE, encountered=False),
        EncounteredColor(color=RED, encountered=False),
    ],
    # DIF
    [
        EncounteredColor(color=YELLOW, encountered=False),
        EncounteredColor(color=RED, encountered=False),
        EncounteredColor(color=BLUE, encountered=False),
    ],
]

moderator_message = [
    "01001001",
    "00100000",
    "01000001",
    "01001101",
    "00100000",
    "01010100",
    "01001000",
    "01000101",
    "00100000",
    "01001101",
    "01001111",
    "01000100",
    "01000101",
    "01010010",
    "01000001",
    "01010100",
    "01001111",
    "01010010",
]


def binary_message_generator(message):
    for msg in message:
        yield binary_to_color(msg)


def binary_to_color(bin: str) -> dict[int, Color]:
    byte = {i: (WHITE if letter == "1" else BLACK) for i, letter in enumerate(bin)}

    # Just fill the remaining lamps with black
    byte[8] = BLACK
    byte[9] = BLACK

    return byte


def reset_forbidden():
    for i in range(len(forbidden_color_groups)):
        for j in range(len(forbidden_color_groups[i])):
            forbidden_color_groups[i][j].encountered = False


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


def matches_pattern(
    colors: dict[int, Color], forbidden_group: list[EncounteredColor]
) -> bool:
    """
    Colors matches forbidden_group if every color is_same as one of the colors in forbidden_group,
    and all colors in forbidden_group have been seen
    """
    for color in colors.values():
        is_forbidden = False
        for i, forbidden_color in enumerate(forbidden_group):
            if is_same(forbidden_color.color, color):
                # We encountered one of the forbidden colors
                forbidden_group[i].encountered = True
                is_forbidden = True
                break
        if not is_forbidden:
            # This color is not one of the forbidden ones, so does not match the pattern
            return False
    # If all was encountered, it's a match!
    return all(x.encountered for x in forbidden_group)


def should_replace_color(colors: dict[int, Color]) -> bool:
    # For every forbidden color
    for i, forbidden_color_group in enumerate(forbidden_color_groups):
        if matches_pattern(colors, forbidden_color_group):
            reset_forbidden()
            return True

    reset_forbidden()

    return False


def is_same(reference, observed) -> bool:
    distance = hue_distance(observed, reference)

    same_hue = distance < HUE_LIMIT
    ref_bright = all(c > 200 for c in reference)
    ref_dark = all(c < 20 for c in reference)
    both_bright = all(c > 200 for c in observed) and ref_bright
    both_dark = all(c < 20 for c in observed) and ref_dark
    return (
        both_bright or both_dark or ((not ref_bright) and (not ref_dark) and same_hue)
    )


def verify_forbidden_colors():
    for i, fcg in enumerate(forbidden_color_groups):
        for j, c1 in enumerate(fcg):
            for k, c2 in enumerate(fcg):
                if j >= k:
                    continue
                if is_same(c1.color, c2.color):
                    print(f"{i} has a contradiction between {c1.color} and {c2.color}")

    for g in forbidden_color_groups:
        color = {i: c.color for i, c in enumerate(g)}
        assert should_replace_color(color)
        reset_forbidden()

    # These colors should definitely pass
    test_passing_colors = ({0: BLACK},)

    for c in test_passing_colors:
        assert not should_replace_color(c)
        reset_forbidden()


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
