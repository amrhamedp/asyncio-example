import asyncio
import concurrent.futures
from datetime import datetime
import time


def anything(i):
    print(i, datetime.now())
    time.sleep(i)


def main():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as e:
        tasks = [loop.run_in_executor(e, anything, i) for i in range(1, 4)]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
