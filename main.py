import os
import requests as r
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Optional
import json
import time
import logging

from models import GetColorState, Color, LockResponse
from colors import (
    should_replace_color,
    binary_message_generator,
    moderator_message,
)

import db


logging.basicConfig(
    filename="color_controller.log",
    format="%(levelname)s\t%(asctime)s\t%(message)s",
    level=logging.INFO,
)


REQUEST_DELAY = 1.0
COLOR_DELAY = 2
# If currently busy, wait this long
# Should be shorter than one second to hopefully go faster than everyone else
BUSY_INCALL_WAIT = 1.0
# If it's currently day, wait for this long
DAY_WAIT = 240
# If we can change the color, but the color is ok, check again in this long
OK_COLOR_WAIT = 30


BASE_API_URL = os.environ["BASE_API_URL"]


# Setup the global http session
retry_strategy = Retry(total=10, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry_strategy)
sess = r.Session()
sess.mount("https://", adapter)
sess.mount("http://", adapter)


def get_colors() -> GetColorState:
    res = sess.get(BASE_API_URL + "getColours")
    try:
        s = GetColorState(**res.json())
    except json.decoder.JSONDecodeError as e:
        logging.error(f"failed to decode json body: {res.text}")
        raise e
    return s


def request_lock() -> Optional[LockResponse]:
    res = sess.get(BASE_API_URL + "requestLock")
    if res.status_code != 200:
        logging.error(f"failed to get request lock with text: {res.text}")
        return None
    return LockResponse(**res.json())


def set_colors(hash: str, colors: dict[int, Color]):
    color_string = json.dumps(colors)
    sess.get(
        BASE_API_URL + "setColours", params={"hash": hash, "colours": color_string}
    )


def main_loop():
    # Start as true to make save on initialization
    waitingForBusy = False

    while True:
        try:
            get_colors_state = get_colors()

            if get_colors_state.isDay:
                logging.debug(f"is day: waiting for {DAY_WAIT}")
                time.sleep(DAY_WAIT)
                continue

            if get_colors_state.isBusy or get_colors_state.inCall:
                logging.debug(f"is buisy: waiting for {BUSY_INCALL_WAIT}")
                waitingForBusy = True
                time.sleep(BUSY_INCALL_WAIT)
                continue

            should_replace = should_replace_color(get_colors_state.colours)

            if waitingForBusy:
                logging.debug("storing shit")
                db.store_color(get_colors_state.colours, should_replace)

            # See if the current color is one that we want to change
            if not should_replace:
                logging.debug(f"is free with ok-color: waiting for {OK_COLOR_WAIT}")
                time.sleep(OK_COLOR_WAIT)
                continue

            logging.info(f"replacing color {get_colors_state.colours}")

            lr = request_lock()
            if lr is None:
                time.sleep(REQUEST_DELAY)
                continue

            # for i in range(150):
            #     set_colors(lr.hash, rainbow(i))
            #     time.sleep(COLOR_DELAY)

            for color in binary_message_generator(moderator_message):
                set_colors(lr.hash, color)
                time.sleep(COLOR_DELAY)

            logging.info("finished setting colors")
        except Exception as e:
            logging.warning(f"recieved error: {e}")


if __name__ == "__main__":
    db.init()

    main_loop()
