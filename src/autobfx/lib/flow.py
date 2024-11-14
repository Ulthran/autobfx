from prefect import flow, tags
from typing import Iterable
from autobfx.lib.config import Config
from autobfx.lib.task import AutobfxTask


class AutobfxFlow:
    def __init__(self, config: Config, name: str, tasks: list[AutobfxTask]):
        self.config = config
        self.name = name
        self.tasks = tasks
