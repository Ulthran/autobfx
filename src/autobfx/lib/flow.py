from autobfx.lib.config import Config
from autobfx.lib.task import AutobfxTask


class AutobfxFlow:
    def __init__(self, config: Config, name: str, tasks: list[AutobfxTask]):
        self.config = config
        self.name = name
        self.tasks = tasks

    # TODO: This class needs to be reworked so that it can represent any portion of a flow
    # that means it needs to expose a variable number of connectors on either end
    # The principle components should be the flow itself and the iterators it expands over (expansion behavior is defined in the flow)
    # It can then be connected (partially or fully) with another flow(s)
