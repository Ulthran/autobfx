import pkgutil


class PluginRegistry:
    def __init__(self):
        self.plugins = {}

    def register(self, plugin):
        self.plugins[plugin.name] = plugin

    def get(self, name):
        return self.plugins.get(name)

    def get_all(self):
        return self.plugins.values()

    def collect(self):
        """Plugins are assumed to be `pip` installed packages named `autobfx-plugin-...`"""
        for moduleinfo in pkgutil.iter_modules():
            if (
                not moduleinfo.name.startswith("autobfx_plugin_")
                or not moduleinfo.ispkg
            ):
                continue

            module = moduleinfo.module_finder.find_module(moduleinfo.name).load_module()
            plugin = module.Plugin()
            self.register(plugin)
