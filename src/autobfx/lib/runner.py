import os
from abc import ABC, abstractmethod
from prefect_shell import ShellOperation
from typing import Type


class RunnerOptions:
    def __init__(self, conda_env: str = "", docker_img: str = ""):
        self.conda_env = conda_env
        self.docker_img = docker_img


class AutobfxSoftwareManager(ABC):
    def __init__(self):
        self.name = "abstract"
        # TODO: Consider adding options for the manager as a whole as well

    @abstractmethod
    def run_cmd(self, cmd: list[str], options: dict = {}):
        pass

    @abstractmethod
    def run_func(
        self,
        func: callable,
        func_args: list = [],
        func_kwargs: dict = {},
        options: dict = {},
    ):
        pass


class NoManager(AutobfxSoftwareManager):
    def __init__(self):
        self.name = "none"

    def run_cmd(self, cmd: list[str], options: dict = {}):
        print(f"Running: {' '.join(cmd)}")

        with ShellOperation(
            commands=[
                " ".join(cmd),
            ],
        ) as shell_operation:
            shell_process = shell_operation.trigger()
            shell_process.wait_for_completion()

    def run_func(
        self,
        func: callable,
        func_args: list = [],
        func_kwargs: dict = {},
        options: dict = {},
    ):
        print(
            f"Running func {func.__name__} with args {func_args} and kwargs {func_kwargs}"
        )

        func(*func_args, **func_kwargs)


class VenvManager(AutobfxSoftwareManager):
    def __init__(self):
        self.name = "venv"

    def run_cmd(self, cmd: list[str], options: dict = {}):
        try:
            venv = options["venv"]
        except KeyError:
            raise KeyError("VenvManager requires a venv key in options")

        print(f"Running (in {venv} venv): {' '.join(cmd)}")

        with ShellOperation(
            commands=[
                f"source {options['venv']}/bin/activate",
                " ".join(cmd),
            ],
        ) as shell_operation:
            shell_process = shell_operation.trigger()
            shell_process.wait_for_completion()

    def run_func(
        self,
        func: callable,
        func_args: list = [],
        func_kwargs: dict = {},
        options: dict = {},
    ):
        print(
            f"Running func {func.__name__} with args {func_args} and kwargs {func_kwargs}"
        )

        pass  # TODO


class CondaManager(AutobfxSoftwareManager):
    def __init__(self):
        self.name = "conda"

    def run_cmd(self, cmd: list[str], options: dict[str, str]):
        try:
            env = options["conda_env"]
        except KeyError:
            raise KeyError("CondaManager requires a conda_env key in options")

        try:
            solver_cmd = options["solver"]
        except KeyError:
            solver_cmd = "conda"

        print(f"Running (in {env} conda env): {' '.join(cmd)}")

        with ShellOperation(
            commands=[
                f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
                f"{solver_cmd} activate {env}",
                " ".join(cmd),
            ],
        ) as shell_operation:
            shell_process = shell_operation.trigger()
            shell_process.wait_for_completion()

    def run_func(
        self,
        func: callable,
        func_args: list = [],
        func_kwargs: dict = {},
        options: dict = {},
    ):
        pass  # TODO


class MambaManager(CondaManager):
    def __init__(self):
        self.name = "mamba"

    def run_cmd(self, cmd: list[str], options: dict = {}):
        options["solver"] = self.name
        super.run_cmd(cmd, options)

    def run_func(
        self,
        func: callable,
        func_args: list = [],
        func_kwargs: dict = {},
        options: dict = {},
    ):
        options["solver"] = self.name
        super().run_func(func, func_args, func_kwargs, options)


class DockerManager(AutobfxSoftwareManager):
    def __init__(self):
        self.name = "docker"

    def run_cmd(self, cmd: list[str], options: dict = {}):
        try:
            img = options["docker_img"]
        except KeyError:
            raise KeyError("DockerManager requires a docker_img key in options")

        print(f"Running (in {img} docker img): {' '.join(cmd)}")

        with ShellOperation(
            commands=[
                f"docker run -v {os.getcwd()}:/data -w /data {img} {' '.join(cmd)}",
            ],
        ) as shell_operation:
            shell_process = shell_operation.trigger()
            shell_process.wait_for_completion()

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        pass  # TODO


class AutobfxRunner(ABC):
    def __init__(self, swm: AutobfxSoftwareManager, options: dict = {}):
        self.name = "abstract"
        self.swm = swm
        self.options = options

    @abstractmethod
    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)
        self.swm.run_cmd(cmd, opts)

    @abstractmethod
    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        opts = self.options.copy()
        opts.update(options)
        self.swm.run_func(func, args=args, kwargs=kwargs, options=opts)

    # TODO: Consider a run_script method, not sure I really care though, either a func or a cmd gives plenty of flexibility


class DryRunner(AutobfxRunner):
    def __init__(self, swm: AutobfxSoftwareManager, options: dict = {}):
        self.name = "dryrun"
        self.swm = swm
        self.options = options

    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)
        print(
            f"Would run (with {self.swm.name} manager and options {opts}): {' '.join(cmd)}"
        )
        return 1

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        opts = self.options.copy()
        opts.update(options)
        print(
            f"Would run func {func.__name__} with args {args} and kwargs {kwargs} with {self.swm.name} manager and options {opts}"
        )
        return 1


class LocalRunner(AutobfxRunner):
    def __init__(self, swm: AutobfxSoftwareManager, options: dict = {}):
        self.name = "local"
        self.swm = swm
        self.options = options

    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)
        self.swm.run_cmd(cmd, opts)
        return 1  # TODO: Return something useful

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        opts = self.options.copy()
        opts.update(options)
        self.swm.run_func(func, args=args, kwargs=kwargs, options=opts)
        return 1


# TODO: Make proper registries for these (and flows) for plugins to work with
swm_map: dict[str, Type[AutobfxSoftwareManager]] = {
    "none": NoManager,
    "venv": VenvManager,
    "conda": CondaManager,
    "mamba": MambaManager,
}


runner_map: dict[str, Type[AutobfxRunner]] = {
    "local": LocalRunner,
    "dryrun": DryRunner,
}


class TestRunner(AutobfxRunner):
    def __init__(
        self,
        run_cmd: callable,
        run_func: callable,
        swm: AutobfxSoftwareManager = NoManager(),
        options: dict = {},
    ):
        self.name = "test"
        self._run_cmd = run_cmd
        self._run_func = run_func
        self.swm = swm
        self.options = options

    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)
        return self._run_cmd(cmd, opts)

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        opts = self.options.copy()
        opts.update(options)
        return self._run_func(func, args=args, kwargs=kwargs, options=opts)
