import os
import subprocess
import time
from abc import ABC, abstractmethod
from prefect_shell import ShellOperation
from simple_slurm import Slurm
from typing import Type


class RunnerOptions:
    def __init__(self, conda_env: str = "", docker_img: str = ""):
        self.conda_env = conda_env
        self.docker_img = docker_img


class AutobfxSoftwareManager(ABC):
    def __init__(self):
        self.name = "abstract"
        # TODO: Consider adding options for the manager as a whole as well

    # TODO: Consider renaming this to something like 'get_run_cmds'
    @abstractmethod
    def run_cmd(self, cmd: list[str], options: dict = {}) -> list[str]:
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

    def run_cmd(self, cmd: list[str], options: dict = {}) -> list[str]:
        return [" ".join(cmd)]

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

    def _prep(self, options: dict = {}) -> str:
        try:
            venv = options["venv"]
        except KeyError:
            raise KeyError("VenvManager requires a venv key in options")

        return venv

    def run_cmd(self, cmd: list[str], options: dict = {}) -> list[str]:
        venv = self._prep(options)

        return [
            f"source {options['venv']}/bin/activate",
            " ".join(cmd),
        ]

    def run_func(
        self,
        func: callable,
        func_args: list = [],
        func_kwargs: dict = {},
        options: dict = {},
    ):
        pass  # TODO


class CondaManager(AutobfxSoftwareManager):
    def __init__(self):
        self.name = "conda"

    def _prep(self, options: dict = {}) -> tuple[str, str]:
        try:
            env = options["conda_env"]
        except KeyError:
            raise KeyError("CondaManager requires a conda_env key in options")

        try:
            solver_cmd = options["solver"]
        except KeyError:
            solver_cmd = "conda"

        return env, solver_cmd

    def run_cmd(self, cmd: list[str], options: dict[str, str]) -> list[str]:
        env, solver_cmd = self._prep(options)

        return [
            f"source {os.environ.get('CONDA_PREFIX', '')}/etc/profile.d/conda.sh",
            f"{solver_cmd} activate {env}",
            " ".join(cmd),
        ]

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

    def run_cmd(self, cmd: list[str], options: dict = {}) -> list[str]:
        options["solver"] = self.name
        return super().run_cmd(cmd, options)

    def run_func(
        self,
        func: callable,
        func_args: list = [],
        func_kwargs: dict = {},
        options: dict = {},
    ):
        pass


class DockerManager(AutobfxSoftwareManager):
    def __init__(self):
        self.name = "docker"

    def _prep(self, options: dict = {}) -> str:
        try:
            img = options["docker_img"]
        except KeyError:
            raise KeyError("DockerManager requires a docker_img key in options")

        return img

    def run_cmd(self, cmd: list[str], options: dict = {}):
        img = self._prep(options)

        # TODO: Figure out how to do this right
        return [f"docker run -v {os.getcwd()}:/data -w /data {img} {' '.join(cmd)}"]

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        pass  # TODO


class AutobfxRunner(ABC):
    def __init__(self, swm: AutobfxSoftwareManager, options: dict = {}):
        self.name = "abstract"
        self.work_pool_name = "default"
        self.worker_type = "process"
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
        self.work_pool_name = "default"
        self.worker_type = "process"
        self.swm = swm
        self.options = options
        print(f"DryRunner initialized with options: {options}")

    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)

        print(f"Would run: {self.swm.run_cmd(cmd, opts)}")
        return 1

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        opts = self.options.copy()
        opts.update(options)

        print(
            f"Would run func {func.__name__} with args {args} and kwargs {kwargs} with options {opts}"
        )
        return 1


class LocalRunner(AutobfxRunner):
    def __init__(self, swm: AutobfxSoftwareManager, options: dict = {}):
        self.name = "local"
        self.work_pool_name = "default"
        self.worker_type = "process"
        self.swm = swm
        self.options = options

    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)

        print(f"Running: {cmd}")
        with ShellOperation(
            commands=self.swm.run_cmd(cmd, opts),
        ) as shell_operation:
            shell_process = shell_operation.trigger()
            shell_process.wait_for_completion()

        return 1  # TODO: Return something useful

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        pass  # TODO


class SLURMRunner(AutobfxRunner):
    def __init__(self, swm: AutobfxSoftwareManager, options: dict = {}):
        self.name = "slurm"
        self.work_pool_name = "slurm"
        self.worker_type = "process"
        self.swm = swm
        self.options = options

    def _wait_for_job_completion(self, job_id: int) -> bool:
        sacct_results = subprocess.run(
            ["sacct", "-j", job_id, "--format=JobID,State,ExitCode"]
        )
        try:
            if sacct_results.stdout.splitlines()[2].split()[1] in [
                "COMPLETED",
                "FAILED",
                "CANCELLED",
                "TIMEOUT",
                "NODE_FAIL",
            ]:
                return True
            return False
        except Exception as e:
            print(f"Error checking job status: {e}")
            return False

    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)
        # params is a RunnerConfig object from the flow config
        # It can't be imported here because it would create a circular import
        params = opts["params"]

        slurm = Slurm(
            cpus_per_task=params.threads,
            mem=f"{params.mem_mb}M",
            time=params.runtime_min,
            job_name=opts["job_name"],
            output=f"%x-%j.out",
        )

        cmds = self.swm.run_cmd(cmd, opts)
        for cmd in cmds[:-1]:
            slurm.add_cmd(cmd)
        job_id = slurm.sbatch(
            cmds[-1],
            sbatch_cmd=params.parameters.get(
                "sbatch_cmd", "/home/ctbus/Penn/autobfx/slurm/sbatch"
            ),
        )

        # Wait for job to finish
        while not self._wait_for_job_completion(job_id):
            time.sleep(10)

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        pass


class ECSRunner(AutobfxRunner):
    def __init__(self, swm: AutobfxSoftwareManager, options: dict = {}):
        self.name = "ecs"
        self.work_pool_name = "ecs"
        self.worker_type = "ecs"
        self.swm = swm
        self.options = options

    def run_cmd(self, cmd: list[str], options: dict = {}):
        opts = self.options.copy()
        opts.update(options)

        print("NOT IMPLEMENTED")

    def run_func(
        self, func: callable, args: list = [], kwargs: dict = {}, options: dict = {}
    ):
        pass


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
    "slurm": SLURMRunner,
    "ecs": ECSRunner,
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
