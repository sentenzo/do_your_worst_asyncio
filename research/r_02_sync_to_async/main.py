import time
import asyncio

from research.helpers.timeit import timeit


@timeit
async def non_blocking():
    print(f"{time.ctime()} Hello!")
    await asyncio.sleep(2.0)
    print(f"{time.ctime()} Goodbye!")


@timeit
def blocking():
    print(f"{time.ctime()} Hello from a blocking code!")
    time.sleep(1)
    print(f"{time.ctime()} Goodbye from a blocking code!")


@timeit
async def main():
    task1 = asyncio.create_task(asyncio.to_thread(blocking))
    task2 = asyncio.create_task(non_blocking())
    await task1
    await task2


if __name__ == "__main__":
    asyncio.run(main())
