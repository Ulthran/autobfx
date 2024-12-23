import pkgutil
from autobfx.flows import CorePlugin
from autobfx.lib.plugin import AutobfxPlugin


class PluginRegistry:
    def __init__(self):
        self.plugins: dict[str, AutobfxPlugin] = {"core": CorePlugin()}

    def register(self, plugin):
        self.plugins[plugin.name] = plugin

    def unregister(self, name):
        del self.plugins[name]

    def unregister_all(self):
        self.plugins = {"core": CorePlugin()}

    def get(self, name):
        return self.plugins.get(name)

    def get_all(self):
        return self.plugins.values()

    def get_flow(self, plugin_name, flow_name):
        return self.get(plugin_name).get_flow[flow_name]

    def collect(self):
        """Plugins are assumed to be `pip` installed packages named `autobfx-plugin-...`"""
        self.unregister_all()

        for moduleinfo in pkgutil.iter_modules():
            if (
                not moduleinfo.name.startswith("autobfx_plugin_")
                or not moduleinfo.ispkg
            ):
                continue

            module = moduleinfo.module_finder.find_module(moduleinfo.name).load_module()
            plugin = module.Plugin()
            self.register(plugin)
