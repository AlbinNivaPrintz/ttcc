import sqlite3
import datetime

from models import Color

con = sqlite3.connect("colours.db", detect_types=sqlite3.PARSE_DECLTYPES)

cur = con.cursor()


def init():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Colors (
            created_at DATETIME,
            was_replaced BOOLEAN,
            "0_r" INT,
            "0_g" INT,
            "0_b" INT,
            "1_r" INT,
            "1_g" INT,
            "1_b" INT,
            "2_r" INT,
            "2_g" INT,
            "2_b" INT,
            "3_r" INT,
            "3_g" INT,
            "3_b" INT,
            "4_r" INT,
            "4_g" INT,
            "4_b" INT,
            "5_r" INT,
            "5_g" INT,
            "5_b" INT,
            "6_r" INT,
            "6_g" INT,
            "6_b" INT,
            "7_r" INT,
            "7_g" INT,
            "7_b" INT,
            "8_r" INT,
            "8_g" INT,
            "8_b" INT,
            "9_r" INT,
            "9_g" INT,
            "9_b" INT
            )
    """
    )


def colors_to_db_format(colors: dict[int, Color]) -> list[int]:
    data = []

    for i in range(10):
        color = colors[i]
        data.extend(color)

    assert len(data) == 30

    return data


def store_color(color: dict[int, Color], was_replaced: bool):
    db_encoded_color = colors_to_db_format(color)

    data = (
        datetime.datetime.now(datetime.timezone.utc),
        was_replaced,
        *db_encoded_color,
    )

    cur.execute(
        """
        INSERT INTO Colors VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        data,
    )
    con.commit()


def get_colors(n_rows: int):
    res = cur.execute(
        """
        SELECT * FROM Colors limit ?;
        """,
        (n_rows,),
    )

    structured_data: list[
        tuple[
            datetime.datetime,
            bool,
            Color,
            Color,
            Color,
            Color,
            Color,
            Color,
            Color,
            Color,
            Color,
            Color,
        ]
    ] = []
    data = res.fetchall()
    for row in data:
        structured_row = (
            row[0],
            bool(row[1]),
            *[(row[i], row[i + 1], row[i + 2]) for i in range(2, 32, 3)],
        )
        structured_data.append(structured_row)
    return structured_data
