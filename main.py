import os
import requests as r
from typing import Optional
import json
import time
import logging

from models import GetColorState, Color, LockResponse
from colors import (
    rainbow,
    should_replace_color,
)


logging.basicConfig(
    filename="color_controller.log",
    format="%(levelname)s\t%(asctime)s\t%(message)s",
    level=logging.INFO,
)


REQUEST_DELAY = 0.5
COLOR_DELAY = 2
# If currently busy, wait this long
# Should be shorter than one second to hopefully go faster than everyone else
BUSY_INCALL_WAIT = 0.9
# If it's currently day, wait for this long
DAY_WAIT = 120
# If we can change the color, but the color is ok, check again in this long
OK_COLOR_WAIT = 30


BASE_API_URL = os.environ["BASE_API_URL"]


def get_colors() -> GetColorState:
    res = r.get(BASE_API_URL + "getColours")
    s = GetColorState(**res.json())
    return s


def request_lock() -> Optional[LockResponse]:
    res = r.get(BASE_API_URL + "requestLock")
    if res.status_code != 200:
        logging.error(f"failed to get request lock with text: {res.text}")
        return None
    return LockResponse(**res.json())


def set_colors(hash: str, colors: dict[int, Color]):
    color_string = json.dumps(colors)
    r.get(BASE_API_URL + "setColours", params={"hash": hash, "colours": color_string})


def main_loop():
    get_colors_state = get_colors()

    if get_colors_state.isDay:
        logging.debug(f"is day: waiting for {DAY_WAIT}")
        time.sleep(DAY_WAIT)
        return

    if get_colors_state.isBusy or get_colors_state.inCall:
        logging.debug(f"is buisy: waiting for {BUSY_INCALL_WAIT}")
        time.sleep(BUSY_INCALL_WAIT)
        return

    # See if the current color is one that we want to change
    if not should_replace_color(get_colors_state.colours):
        logging.debug(f"is free with ok-color: waiting for {OK_COLOR_WAIT}")
        time.sleep(OK_COLOR_WAIT)
        return

    logging.info(f"replacing color {get_colors_state.colours}")

    lr = request_lock()
    if lr is None:
        time.sleep(REQUEST_DELAY)
        return

    for i in range(150):
        set_colors(lr.hash, rainbow(i))
        time.sleep(COLOR_DELAY)

    logging.info("finished setting colors")


if __name__ == "__main__":
    while True:
        main_loop()
