import marimo

__generated_with = "0.14.0"
app = marimo.App(width="medium")

with app.setup:
    import asyncio
    import time

    import httpx
    import marimo as mo

    async def async_spam(sleep_for):
        await asyncio.sleep(sleep_for)
        return sleep_for

    def spam(sleep_for):
        time.sleep(sleep_for)
        return sleep_for


@app.cell
def _():
    mo.md(r"""# How the event loop works""")
    return


@app.class_definition
class MinimalEventLoop:
    def __init__(self):
        self.ready = []
        self.next = []

    def run_almost_forever(self):
        while self.ready or self.next:
            for callback, args in self.ready:
                callback(*args)
            self.ready = self.next
            self.next = []
        print("Done")

    def schedule(self, callback, *args):
        self.next.append((callback, args))


@app.cell
def _():
    loop = MinimalEventLoop()

    def run_eventually(i):
        print(f"Running {i}!")
        if i % 2 == 0:
            loop.schedule(run_eventually, i - 1)
        return spam(1)

    loop.schedule(run_eventually, 1)
    loop.schedule(run_eventually, 2)
    loop.run_almost_forever()
    return


@app.cell
def _():
    mo.md(
        r"""
    ## Now with generators
    Check out
    [this cool article](https://dev.indooroutdoor.io/asyncio-demystified-rebuilding-it-from-scratch-one-yield-at-a-time)
    to go deeper into this topic.
    """
    )
    return


@app.cell
def _():
    class Task:
        def __init__(self, coro):
            self._coro = coro
            self.value = None

        def run(self):
            return self._coro.send(self.value)

    class GeneratorEventLoop:
        def __init__(self):
            self.ready = []
            self.next = []

        def run_almost_forever(self):
            while self.ready or self.next:
                for task in self.ready:
                    try:
                        task.run()
                        self.next.append(task)
                    except StopIteration as stop:
                        task.value = stop.value
                self.ready = self.next
                self.next = []

        def schedule(self, coro):
            task = Task(coro)
            self.next.append(task)
            return task

    return (GeneratorEventLoop,)


@app.cell
def _(GeneratorEventLoop):
    def _almost_a_coroutine(max):
        print("started")
        for i in range(max):
            print(f"doing stuff before {i=}")
            time.sleep(0.5)
            yield i
        print("one more yield")
        yield
        print("done")
        return max

    gen_loop = GeneratorEventLoop()
    t = gen_loop.schedule(_almost_a_coroutine(3))
    gen_loop.run_almost_forever()
    print(f"{t.value=}")
    return


@app.cell
def _():
    mo.md(
        r"""
    # The right tools
    ## Common async code smells
    """
    )
    return


@app.cell
async def _():
    async def _shouldnt_be_a_coroutine(max_val):
        sum = 0
        for i in range(max_val):
            sum += 0.1 * i
        return sum

    async def all_the_bad_things():
        sum_result = await _shouldnt_be_a_coroutine(2**10)
        blocking_result = spam(1)  # async_spam is available!

        result_1 = await async_spam(0.5)
        result_2 = await async_spam(0.6)

        values = []
        for i in range(10):
            value = await async_spam(0.1 * i)
            values.append(value)

        return sum_result + blocking_result + result_1 + result_2 + sum(values)

    _start = time.time()
    _result = await all_the_bad_things()
    _end = time.time()
    print(f"done in {_end - _start:.5f} seconds")
    print(f"{_result=}")
    return


@app.cell
def _():
    mo.md(r"""## Using `asyncio.gather`""")
    return


@app.cell
def _():
    async def bad_loop():
        for _ in range(100):
            await asyncio.sleep(0.1)

    async def good_gather():
        tasks = [asyncio.sleep(0.1) for i in range(100)]
        await asyncio.gather(*tasks)

    return bad_loop, good_gather


@app.cell
async def _(bad_loop):
    _start = time.time()
    await bad_loop()
    _end = time.time()
    print(f"done in {_end - _start:.5f} seconds")
    return


@app.cell
async def _(good_gather):
    _start = time.time()
    await good_gather()
    _end = time.time()
    print(f"done in {_end - _start:.5f} seconds")
    return


@app.cell
async def _():
    async def get_joke(id):
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://official-joke-api.appspot.com/jokes/{id}")
        if r.status_code >= 400:
            raise Exception(f"Joke {id=} not found")
        await r.aread()
        data = r.json()
        return f"{data['setup']} {data['punchline']}"

    async def get_jokes():
        tasks = [get_joke(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print("Failed:", result)
            else:
                print(result)

    await get_jokes()
    return


@app.cell
def _():
    mo.md(r"""## Using `asyncio.create_task`""")
    return


@app.cell
async def _():
    tasks = set()  # for keeping a reference

    async def something_i_need_now():
        await async_spam(0.1)
        print("here you go")

    async def something_that_can_run_later():
        print("starting")
        await async_spam(1)
        print("Did the thing!")
        return 0

    def mark_done(task):
        global tasks
        tasks.remove(task)
        print(f"Finished {task.get_name()}")

    async def run():
        task = asyncio.create_task(something_that_can_run_later(), name="later_task")
        task.add_done_callback(mark_done)
        tasks.add(task)

        await something_i_need_now()

        while not task.done():
            await asyncio.sleep(0.5)

        if task.done():
            print(f"Result={task.result()}")

    await run()
    return


@app.cell
def _():
    mo.md(r"""## Using `asyncio.TaskGroup`""")
    return


@app.cell
def _():
    async def get_data():
        print("getting data...")
        await async_spam(1)
        print("got data")
        return [0, 1, 2, 3, 4, 5]

    async def get_size():
        print("getting size...")
        await async_spam(0.1)
        print("got size")
        return 6

    async def bad_awaits():
        data = await get_data()
        size = await get_size()
        print(f"{data=}, {size=}")

    async def gather():
        results = await asyncio.gather(*[get_data(), get_size()])
        # Yes, this particular example could be done with
        # data, size = await asyncio.gather(get_data(), get_size())
        # It's not the point of this example

        # Not very readable or idiomatic. Imagine needing to modify or format separately
        print(f"data={results[0]}, size={results[1]}")

    async def task_group():
        # Now this is nice
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(get_data())
            t2 = tg.create_task(get_size())

        data = t1.result()
        size = t2.result()

        print(f"{data=}, {size=}")

    return bad_awaits, gather, task_group


@app.cell
async def _(bad_awaits):
    # Not really async, see?
    await bad_awaits()
    return


@app.cell
async def _(gather):
    # I bet *this* is what you expect from async code :)
    await gather()
    return


@app.cell
async def _(task_group):
    # Same async, nicer and more manageable
    await task_group()
    return


@app.cell
def _():
    mo.md(r"""## Fixing the code smells""")
    return


@app.cell
async def _():
    def _not_actually_a_coroutine(max_val):
        sum = 0
        for i in range(max_val):
            sum += 0.1 * i
        return sum

    async def actually_a_coroutine(max_val):
        return await asyncio.gather(*[async_spam(0.1 * i) for i in range(max_val)])

    async def all_the_good_things():
        value = _not_actually_a_coroutine(2**10)

        async with asyncio.TaskGroup() as tg:
            long_result = tg.create_task(async_spam(1))
            result_1 = tg.create_task(async_spam(0.5))
            result_2 = tg.create_task(async_spam(0.6))
            values = tg.create_task(actually_a_coroutine(10))

        return (
            value
            + long_result.result()
            + result_1.result()
            + result_2.result()
            + sum(values.result())
        )

    _start = time.time()
    _result = await all_the_good_things()
    _end = time.time()
    print(f"done in {_end - _start:.5f} seconds")
    print(f"{_result=}")
    return


@app.cell
def _():
    mo.md(
        r"""
    # Never go fully async
    ## Using `asyncio.Semaphore`
    """
    )
    return


@app.cell
def _():
    class MyCoolService:
        max_size = 10

        def __init__(self):
            self.current_services = set()

        async def my_slow_action(self, id):
            if len(self.current_services) > self.max_size:
                raise RuntimeError("You broke my service :(")
            if id in self.current_services:
                raise ValueError("You already requested this!")
            self.current_services.add(id)
            print(f"starting {id=}")
            await async_spam(2)
            self.current_services.remove(id)
            return id

    service = MyCoolService()
    return (service,)


@app.cell
async def _(service):
    async def unsafe(id):
        return await service.my_slow_action(id)

    try:
        await asyncio.gather(*[unsafe(i) for i in range(20)])
    except RuntimeError as e:
        print(repr(e))
        print("told you!")

    service.current_services.clear()
    return


@app.cell
async def _(service):
    semaphore = asyncio.Semaphore(8)  # less than what the service handles :)

    async def safe(id):
        async with semaphore:
            return await service.my_slow_action(id)

    await asyncio.gather(*[safe(i) for i in range(20)])
    return


if __name__ == "__main__":
    app.run()
