import asyncio
from datetime import datetime

import time


def anything(i):
    print(i, datetime.now())
    time.sleep(i)


def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.call_later(2, loop.stop)
    for i in range(1, 4):
        loop.call_soon(anything, i)
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
