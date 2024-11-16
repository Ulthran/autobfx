from pathlib import Path
from pydantic import BaseModel
from autobfx.lib.runner import (
    AutobfxRunner,
    AutobfxSoftwareManager,
    runner_map,
    swm_map,
)


class FlowConfig(BaseModel):
    # A directory or list of directories containing input reads
    input_reads: Path | str | list[Path | str] = ""
    # A dictionary of extra input names mapping to the input directories or files
    extra_inputs: dict[str, Path | str | list[Path | str]] = {}
    # A directory or list of directories containing output reads
    output_reads: Path | str | list[Path | str] = ""
    # A dictionary of extra output names mapping to the output directories or files
    extra_outputs: dict[str, Path | str | list[Path | str]] = {}
    # TODO: Consider adding flow-level SWM override
    conda: str = "base"
    image: str = ""
    parameters: dict[str, str | int | float | Path | list | dict] = {}

    def _parse_io_dir(self, input_fp: Path, project_fp: Path) -> Path:
        if not input_fp.is_absolute():
            input_fp = project_fp / input_fp

        return input_fp.resolve()

    def get_input_reads(self, project_fp: Path) -> list[Path]:
        if isinstance(self.input_reads, list):
            return [self._parse_io_dir(Path(x), project_fp) for x in self.input_reads]
        return [self._parse_io_dir(Path(self.input_reads), project_fp)]

    def get_extra_inputs(self, project_fp: Path) -> dict[str, list[Path]]:
        extra_inputs = {}
        for k, v in self.extra_inputs.items():
            if isinstance(v, list):
                extra_inputs[k] = [self._parse_io_dir(Path(x), project_fp) for x in v]
            else:
                extra_inputs[k] = [self._parse_io_dir(Path(v), project_fp)]
        return extra_inputs

    def get_output_reads(self, project_fp: Path) -> list[Path]:
        if isinstance(self.output_reads, list):
            return [self._parse_io_dir(Path(x), project_fp) for x in self.output_reads]
        return [self._parse_io_dir(Path(self.output_reads), project_fp)]

    def get_extra_outputs(self, project_fp: Path) -> dict[str, list[Path]]:
        extra_outputs = {}
        for k, v in self.extra_outputs.items():
            if isinstance(v, list):
                extra_outputs[k] = [self._parse_io_dir(Path(x), project_fp) for x in v]
            else:
                extra_outputs[k] = [self._parse_io_dir(Path(v), project_fp)]
        return extra_outputs


class Config(BaseModel):
    version: str
    name: str
    project_fp: Path
    paired_end: bool = True
    log_fp: str | Path = "logs"
    # benchmark_dir: str = "benchmark" # TODO: Is this even a good way of doing this? Explore alternatives
    swm: str = "none"
    runner: str = "local"
    samples: dict[str, Path] = {}
    flows: dict[str, FlowConfig] = (
        {}
    )  # Consider something like 'trimmomatic:param_set_1' as a key that can be parsed to run the same flow with different parameter sets

    def get_log_fp(self) -> Path:
        log_fp = Path(self.log_fp)
        if not log_fp.is_absolute():
            log_fp = self.project_fp / log_fp

        return log_fp

    def get_runner(self, flow_config: FlowConfig) -> AutobfxRunner:
        try:
            swm = swm_map[self.swm]()
        except KeyError:
            raise ValueError(
                f"Software manager {self.swm} type is not supported or is not installed"
            )

        try:
            return runner_map[self.runner](
                swm,
                options={
                    "conda_env": flow_config.conda,
                    "docker_img": flow_config.image,
                },
            )
        except KeyError:
            raise ValueError(
                f"Runner {self.runner} type is not supported or is not installed"
            )
