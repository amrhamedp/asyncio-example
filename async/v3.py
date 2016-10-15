import asyncio
from datetime import datetime

import time


async def anything(i):
    print(i, datetime.now())
    await asyncio.sleep(i)


def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.call_later(2, loop.stop)
    for i in range(1, 4):
        loop.create_task(anything(i))  # instantiating a coroutine
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
