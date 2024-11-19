import os
from pathlib import Path


reads = Path(__file__).parent.parent / "reads"
hosts = Path(__file__).parent.parent / "hosts"
nextera_adapters_fp = (
    Path(os.environ.get("CONDA_PREFIX", ""))
    / "envs"
    / "trimmomatic"
    / "share/trimmomatic/adapters/NexteraPE-PE.fa"
)

config = {
    "version": "0.0.0",
    "name": "example",
    "project_fp": __file__.split("config.py")[0],
    "paired_end": True,
    "log_fp": "logs",
    "runner": "dryrun",
    "swm": "none",
    "flows": {
        "trimmomatic": {
            "input_reads": reads,
            "extra_inputs": {"adapter_template": nextera_adapters_fp},
            "output_reads": ["trimmomatic", "trimmomatic/unpaired"],
            "conda": "trimmomatic",
            "parameters": {"threads": 4},
        },
        "fastqc": {
            "input_reads": "trimmomatic",
            "output_reads": "fastqc",
            "conda": "fastqc",
        },
        "heyfastq": {"input_reads": "trimmomatic", "output_reads": "heyfastq"},
        "build_host_index": {"extra_inputs": {"hosts": hosts}, "conda": "bwa"},
        "align_to_host": {
            "input_reads": "heyfastq",
            "extra_inputs": {"hosts": hosts},
            "output_reads": "align_to_host",
            "conda": "bwa",
        },
        "filter_host_reads": {
            "input_reads": "align_to_host",
            "output_reads": "filter_host_reads",
        },
        "preprocess_report": {
            "input_reads": "filter_host_reads",
            "output_reads": "preprocess_report",
            "conda": "multiqc",
        },
    },
}
