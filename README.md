# How not to write async Python (and what to do instead)

Is asynchronous Python actually speeding up my code? Maybe yes, maybe it's slower and
full of bugs because of it.

### Code

All code shown during the presentation is at [notebook.py](notebook.py). To open it
notebook-style use
```shell
make init
make run
```
which will install [marimo](https://marimo.io/) and open the notebook in your browser.
Make sure you have [uv](https://docs.astral.sh/uv/) installed!

### Slides
WIP

### References
> If I have seen further than others, it is by standing upon the shoulders of giants.
> Isaac Newton

* [Python asyncio source code](https://github.com/python/cpython/tree/3be3c496df3d2ab48d1c66031b9fc78550b3a2a6/Lib/asyncio)
* [Python asyncio docs](https://docs.python.org/3/library/asyncio.html)
* [What the heck is the event loop anyway?](https://www.youtube.com/watch?v=8aGhZQkoFbQ)
* [Demystifying AsyncIO: Building your own event loop in Python](https://www.youtube.com/watch?v=Ww2HBNpu98g)
* [Asyncio Demystified: Rebuilding it From Scratch One Yield at a Time](https://dev.indooroutdoor.io/asyncio-demystified-rebuilding-it-from-scratch-one-yield-at-a-time)
* [FastAPI concurrency and async/await](https://fastapi.tiangolo.com/async/)
