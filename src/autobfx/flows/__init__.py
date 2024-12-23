from autobfx import __version__
from autobfx.flows.bwa import BUILD_HOST_INDEX, ALIGN_TO_HOST
from autobfx.lib.plugin import AutobfxPlugin


class CorePlugin(AutobfxPlugin):
    def __init__(self):
        super().__init__(
            name="core",
            version=__version__,
            description='Core "plugin" for autobfx',
            flows={BUILD_HOST_INDEX},
        )
