import os
import site
from pathlib import Path
from setuptools import setup
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    
    def run(self):
        # Run the standard install process
        install.run(self)
        
        # Define the environment variable in a sitecustomize.py file
        flows_path = Path(os.path.abspath(os.path.dirname(__file__))) / "src" / "autobfx" / "flows"
        sitecustomize_path = os.path.join(site.getsitepackages()[0], 'sitecustomize.py')
        
        with open(sitecustomize_path, 'a') as f:
            f.write(f"\nimport os\nos.environ['AUTOBFX_FLOWS'] = '{flows_path}'\n")


setup(
    cmdclass={
        'install': PostInstallCommand,
    },
)