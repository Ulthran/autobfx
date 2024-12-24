from autobfx.lib.io import IOObject, IOReads
from pathlib import Path


class AutobfxIterator:
    """
    An iterator class for expansion variables on flows
    The `iterable` attribute maps the variable name to the value e.g. "sample": "sample1" for each task

    [{"sample": "sample1", "host": "host1"}, {"sample": "sample1", "host": "host2"}, ...]
    """

    def __init__(self, iterable: list[dict[str, str]]):
        self.iterable = iterable

    def __iter__(self):
        return iter(self.iterable)

    def __str__(self):
        return f"{self.iterable}"

    def degree(self):
        return len(self.iterable[0].items())

    @classmethod
    def gather(
        cls,
        iterable: list[dict[str, str]],
        override: "AutobfxIterator" = None,
    ):
        if override:
            return override

        return AutobfxIterator(iterable)

    @classmethod
    def expand(cls, iterators: list["AutobfxIterator"]):
        """
        Expand multiple iterators into a single iterator
        """
        if not iterators:
            return cls([])
        elif len(iterators) == 1:
            return iterators[0]
        else:
            return cls(
                [
                    {k: v for d in dicts for k, v in d.items()}
                    for dicts in zip(*[i.iterable for i in iterators])
                ]
            )
