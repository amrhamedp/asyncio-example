import asyncio
from datetime import datetime

import time


async def anything(i):
    print(i, datetime.now())
    await asyncio.sleep(i)


def main():
    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    # loop.call_later(2, loop.stop)

    tasks = [loop.create_task(anything(i=i)) for i in range(1, 4)]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
