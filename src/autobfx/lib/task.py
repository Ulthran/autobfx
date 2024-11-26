from pathlib import Path
from prefect import tags, task
from typing import Callable
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.runner import AutobfxRunner, DryRunner, LocalRunner, NoManager


class AutobfxTask:
    """
    A class to represent a task to be executed by autobfx.
    """

    def __init__(
        self,
        name: str,
        ids: list[str],
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
        self.ids = tuple(
            ids
        )  # Any identifiers for the task run e.g. (sample_name) or (sample_name, host_name)
        # self.id_tuple: tuple[str, ...] = tuple(ids.values()) # For use as task tags or composite dictionary key
        self._func = func
        self.project_fp = project_fp
        self.input_reads = input_reads
        self.extra_inputs = {
            k: [IOObject(x) for x in v] for k, v in extra_inputs.items()
        }
        self.output_reads = output_reads
        self.extra_outputs = {
            k: [IOObject(x) for x in v] for k, v in extra_outputs.items()
        }
        self.log_fp = log_fp
        self.runner = runner
        self.runner.options["job_name"] = f"{self.name}_{'_'.join(self.ids)}"
        self.dryrun = True if isinstance(self.runner, DryRunner) else False
        self.args = args
        self.kwargs = kwargs

        self.done_fp = (
            self.project_fp
            / ".autobfx"
            / "done"
            / f".{self.name}_{'_'.join(self.ids)}.done"
        )

        @task(name=self.runner.options["job_name"])
        def _runner_func():
            output = self._func(
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
                self.done_fp.touch()

            return output

        self._runner_func = _runner_func

    def _check(self) -> bool:
        # Will probably want to raise this to the flow level once we figure out more better flow abstraction
        # E.g. checking input files from an S3 bucket for 100 samples
        for input_obj in self.input_reads + [
            i for ioo in self.extra_inputs.values() for i in ioo
        ]:
            if not input_obj.check():
                print(
                    f"{dict(input_obj)} doesn't exist but is listed as an input for {self.name}: {self.ids}"
                )
                return False

        if self.done_fp.exists():
            print(f"Task run marked as already completed by {self.done_fp}")
            return False

        return True

    def _setup_run(self):
        for output_obj in self.output_reads + list(self.extra_outputs.values()):
            if not output_obj.fp.parent.exists():
                output_obj.fp.parent.mkdir(parents=True)

        if not self.log_fp.parent.exists():
            self.log_fp.parent.mkdir(parents=True)

        if not self.done_fp.parent.exists():
            self.done_fp.parent.mkdir(parents=True)

    def _run(self, submit: bool = False, wait_for: list = None):
        if not self.dryrun:
            if not self._check():
                if submit:

                    class AlreadyDone:
                        def result(self):
                            return None

                    return AlreadyDone()
                else:
                    return None

            self._setup_run()

        with tags(self.name, *self.ids):
            if submit:
                return (
                    self._runner_func.submit(wait_for=wait_for)
                    if wait_for
                    else self._runner_func.submit()
                )
            else:
                return self._runner_func()

    def run(self):
        return self._run()

    def submit(self, wait_for: list = None):
        return self._run(submit=True, wait_for=wait_for)
