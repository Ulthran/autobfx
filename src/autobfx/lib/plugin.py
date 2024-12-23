from autobfx.lib.flow import AutobfxFlow


class AutobfxPlugin:
    def __init__(
        self, name: str, version: str, description: str, flows: dict[str, AutobfxFlow]
    ):
        self.name = name
        self.version = version
        self.description = description
        self.flows = flows

    def get_flow(self, flow_name: str) -> AutobfxFlow:
        return self.flows[flow_name]
