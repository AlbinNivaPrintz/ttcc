import typer
from rich import text
from rich.table import Table
from rich.console import Console

from db import get_colors


def seen_colors_table():
    data = get_colors(10)

    table = Table("Date", "Replaced", *[f"Lamp_{i}" for i in range(10)])

    for row in data:
        table_row = [row[0], str(row[1])]
        for i in range(10):
            style = f"rgb({row[2+i][0]},{row[2+i][1]},{row[2+i][2]})"
            lamp = text.Text("■", style=style)
            table_row.append(lamp)
        table.add_row(*table_row)

    return table


def main():
    seen_colors = seen_colors_table()

    console = Console(color_system="truecolor")
    console.print(seen_colors)


if __name__ == "__main__":

    typer.run(main)
