import json
from pathlib import Path
from prefect import tags, task
from pydantic import BaseModel
from typing import Callable
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.runner import AutobfxRunner, DryRunner, LocalRunner, NoManager


class AutobfxTaskDefinition(BaseModel):
    """
    Represents a task definition that hasn't been expanded over any iterators yet.
    """

    name: str
    func: Callable


class AutobfxTask:
    """
    A class to represent a task to be executed by autobfx.
    """

    def __init__(
        self,
        name: str,
        ids: dict[str, str],
        func: Callable,
        project_fp: Path,
        input_reads: list[IOReads] = [],
        extra_inputs: dict[str, list[Path]] = {},
        output_reads: list[IOReads] = [],
        extra_outputs: dict[str, list[Path]] = {},
        log_fp: Path = Path(),
        runner: AutobfxRunner = LocalRunner(swm=NoManager()),
        args: list = [],
        kwargs: dict = {},
    ):
        self.name = name  # The task name e.g. "trimmomatic"
        self.id_dict = ids  # A dictionary of identifiers for the task run e.g. {"sample_name": "sample1", "host_name": "host1"}
        self.ids = tuple(
            ids.values()
        )  # A hashable form of the task ids e.g. (sample_name) or (sample_name, host_name)
        self._func = func
        self.project_fp = project_fp
        self.input_reads = input_reads
        self.extra_inputs = {
            k: [IOObject(x) for x in v] for k, v in extra_inputs.items()
        }
        self.inputs = self.input_reads + [
            i for ioo in self.extra_inputs.values() for i in ioo
        ]
        self.output_reads = output_reads
        self.extra_outputs = {
            k: [IOObject(x) for x in v] for k, v in extra_outputs.items()
        }
        self.outputs = self.output_reads + [
            i for ioo in self.extra_outputs.values() for i in ioo
        ]
        # submission is the Promise that is returned by submitting a task
        # this is used for dependent tasks to wait on the completion of this task
        self.submission = None
        self.log_fp = log_fp
        self.runner = runner
        self.runner.options["job_name"] = f"{self.name}_{'_'.join(self.ids)}"
        self.dryrun = True if isinstance(self.runner, DryRunner) else False
        self.args = args
        self.kwargs = kwargs

        @task(name=self.runner.options["job_name"])
        def _runner_func():
            cmd = self._func(
                self.input_reads,
                self.extra_inputs,
                self.output_reads,
                self.extra_outputs,
                self.log_fp,
                self.runner,
                *self.args,
                **self.kwargs,
            )

            if not self.dryrun:
                for o in self.outputs:
                    with open(o.done_fp, "w") as f:
                        # TODO: Write enough config here to make the step fully reproducible
                        json.dump(self.runner.options, f, default=vars)
                        f.write(f"\ncmd: {cmd}")

            return cmd

        self._runner_func = _runner_func

    def __hash__(self):
        return hash((self.name, self.ids))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def _check(self) -> bool:
        # Will probably want to raise this to the flow level once we figure out more better flow abstraction
        # E.g. checking input files from an S3 bucket for 100 samples
        if not all(i.check() for i in self.inputs):
            print(
                f"{[i for i in self.inputs if not i.check()]} missing but required for {self.name}: {self.ids}"
            )
            return False

        if any(o.done_fp.exists() for o in self.outputs):
            if all(o.done_fp.exists() for o in self.outputs):
                print(
                    f"Task run already completed by {[o.done_fp for o in self.outputs]}"
                )
                return False
            else:
                print(
                    f"Task run marked as partially completed by {[o.done_fp for o in self.outputs if o.done_fp.exists()]}, rerunning to generate all outputs"
                )

        return True

    def _setup_run(self):
        # TODO: Probably need a step here to remove stale outputs before creating empty dirs
        # avoid problems with tools that don't like overwriting existing files (e.g. megahit)
        for o in self.outputs:
            if not o.fp.parent.exists():
                o.fp.parent.mkdir(parents=True)

        if not self.log_fp.parent.exists():
            self.log_fp.parent.mkdir(parents=True)

    def run(self):
        """Ignore dependencies and run the task"""
        if not self.dryrun:
            if not self._check():
                return None

            self._setup_run()

        with tags(self.name, *self.ids):
            return self._runner_func()

    def submit(self, dependencies: list["AutobfxTask"] = []):
        """Submit the task for execution, submitting any dependencies first"""
        if not self.dryrun:
            if not self._check():

                class AlreadyDone:
                    def result(self):
                        return None

                return AlreadyDone()

            self._setup_run()

        with tags(self.name, *self.ids):
            self.submission = self._runner_func.submit(
                wait_for=[d.submission for d in dependencies]
            )
            return self.submission
