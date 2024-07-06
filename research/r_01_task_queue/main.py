import asyncio
from random import random
from asyncio import Queue, CancelledError, Event, QueueEmpty


class Runnable:
    async def run(self) -> None:
        raise NotImplementedError


class Sender(Runnable):
    def __init__(
        self, name: str, queue: Queue, close_event: Event, delay: float
    ) -> None:
        self.name = name
        self.queue = queue
        self.close_event = close_event
        self.delay = delay
        self.msg_counter = 0

    async def send_new_mesage(self) -> None:
        await asyncio.sleep(random() * self.delay)
        self.msg_counter += 1
        msg_text = f"{self.name:>10} - {self.msg_counter:>4}"
        print(msg_text)
        await self.queue.put(msg_text)

    async def run(self) -> None:
        try:
            while True:
                if self.close_event.is_set():
                    print(f"{self.name:>10} - Closing event")
                    break
                await asyncio.shield(
                    self.send_new_mesage()
                )  # must not be interrupted
            print(f"{self.name:>10} - Exit")
        except CancelledError:
            print(f"{self.name:>10} - CancelledError")
            self.close_event.set()


class Receiver(Runnable):
    def __init__(
        self,
        name: str,
        queue: Queue,
        close_event: Event,
        delay: float,
        finalize: bool = False,
    ) -> None:
        self.name = name
        self.queue = queue
        self.close_event = close_event
        self.delay = delay
        self.finalize = finalize

    async def get_message(self) -> str | None:
        while True:
            try:
                return self.queue.get_nowait()
            except QueueEmpty:
                if self.close_event.is_set():
                    return None
                await asyncio.sleep(0.2)

    async def process_message(self, msg: str, suffix: str = "") -> None:
        await asyncio.sleep(random() * self.delay)  # processing
        print(f"\t{self.name:>10} - {msg=}{suffix}")

    async def run(self) -> None:
        try:
            while True:
                msg = await self.get_message()
                if self.close_event.is_set():
                    print(f"\t{self.name:>10} - Closing event")
                    break
                assert msg
                await asyncio.shield(
                    self.process_message(msg)
                )  # must not be interrupted
            await self.finalizer()  # closing event
            print(f"\t{self.name:>10} - Exit")
        except CancelledError:
            print(f"\t{self.name:>10} - CancelledError")
            self.close_event.set()

    async def finalizer(self) -> None:
        while not self.queue.empty():
            msg = await self.get_message()
            if msg:
                await asyncio.shield(self.process_message(msg, "  [finalize]"))


async def main():
    print()
    queue = Queue()
    close_event = Event()
    senders = [
        Sender(f"sender-{i}", queue, close_event, 1.0) for i in range(2)
    ]
    receivers = [
        Receiver(f"receiver-{i}", queue, close_event, 4.0) for i in range(5)
    ]

    tasks = []
    for runner in senders + receivers:
        tasks.append(asyncio.create_task(runner.run()))

    for task in tasks:
        await task

    # async with asyncio.TaskGroup() as tg:
    #     tasks = []
    #     for runner in senders + receivers:
    #         tasks.append(tg.create_task(runner.run()))
    #     await asyncio.wait(tasks)

    print("Queue size:", queue.qsize())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
