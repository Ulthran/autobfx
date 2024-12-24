import networkx as nx
from autobfx.lib.config import Config
from autobfx.lib.io import IOObject, IOReads
from autobfx.lib.iterator import AutobfxIterator
from autobfx.lib.task import AutobfxTask
from pathlib import Path
from prefect import flow


class AutobfxFlow:
    def __init__(self, name: str, dag: nx.DiGraph):
        self.name = name
        self.dag = dag

        # Keeping this in the constructor so that it's easy to run pre/post processing around it down the line
        @flow
        def _flow():
            submissions = [
                t.submit(dependencies=dag.predecessors(t))
                for t in nx.topological_sort(dag)
            ]
            return [s.result() for s in submissions]

        self.flow = _flow

    def __str__(self):
        return (
            f"AutobfxFlow({self.name}): {[(n.name, n.id_dict) for n in self.dag.nodes]}"
        )

    @classmethod
    def from_tasks(cls, name: str, tasks: list[AutobfxTask]) -> "AutobfxFlow":
        """
        Create an unconnected flow from a list of tasks
        """
        dag = nx.DiGraph()
        for task in tasks:
            dag.add_node(task)

        return cls(name, dag)

    @classmethod
    def empty_flow(cls, name: str) -> "AutobfxFlow":
        return cls(name, nx.DiGraph())

    @classmethod
    def compose_flows(cls, name: str, flows: list["AutobfxFlow"]) -> "AutobfxFlow":
        dag = nx.compose_all([flow.dag for flow in flows])
        return cls(name, dag)

    @staticmethod
    def gather_files(
        fp: Path, ext: str, iterator: AutobfxIterator = None
    ) -> dict[str, IOObject]:
        if iterator:
            return {
                v: IOObject(fp / f"{v}.{ext}") for d in iterator for k, v in d.items()
            }
        return {x.stem: x.resolve() for x in fp.glob(f"*.{ext}")}

    @staticmethod
    def gather_samples(
        fp: Path,
        paired_end: bool,
        config_samples: dict[str, tuple[Path, ...]] = None,
        sample_iterator: AutobfxIterator = None,
    ) -> dict[str, IOReads]:
        """
        Gather samples from a directory of fastq files
        - If a value for `sample_iterator` is provided it will use that and `fp` to construct IOReads and return it
        - If a value for `config_samples` is provided it will convert that to IOReads and return it
        - After that it will look for fastq.gz files in `fp` and assume that the sample name is the part of the filename before '_R1' or '.fastq.gz'

        The intended use cases are as follows:
        - If this is a component of another flow and isn't the start, the `sample_iterator` arg will be passed so that we aren't trying to gather samples from a directory that doesn't exist yet
        - If you're trying to run a subset of samples, you can define them in the config and pass them in as `config_samples`
        - Otherwise, this will make it easy to gather samples from a directory of fastq files
        """
        if sample_iterator:
            if paired_end:
                return {
                    d["sample"]: IOReads(
                        fp / f"{d['sample']}_R1.fastq.gz",
                        fp / f"{d['sample']}_R2.fastq.gz",
                    )
                    for d in sample_iterator
                }
            else:
                return {
                    d["sample"]: IOReads(fp / f"{d['sample']}.fastq.gz")
                    for d in sample_iterator
                }
        if config_samples:
            return {k: IOReads(*v) for k, v in config_samples.items()}
        if paired_end:
            r1 = [x.resolve() for x in fp.glob("*.fastq.gz") if "_R1" in x.name]
            r2 = [x.resolve() for x in fp.glob("*.fastq.gz") if "_R2" in x.name]
            sample_names = [x.name.split("_R1")[0] for x in r1]
            sample_names_2 = [x.name.split("_R2")[0] for x in r2]
            if sample_names != sample_names_2:
                print(sample_names)
                print(sample_names_2)
                raise ValueError(f"Sample names do not match in {fp}")
            if len(sample_names) != len(set(sample_names)):
                print(sample_names)
                raise ValueError(
                    f"Duplicate sample names in {fp} (Only what's in front of '_R1'/'_R2' is considered)"
                )

            if len(r1) != len(r2):
                print(r1)
                print(r2)
                raise ValueError(f"Number of R1 and R2 files do not match in {fp}")

            return {x: IOReads(y, z) for x, y, z in zip(sample_names, r1, r2)}
        else:
            r1 = list(fp.glob("*.fastq.gz"))
            sample_names = [x.name.split(".fastq")[0] for x in r1]
            if len(sample_names) != len(set(sample_names)):
                print(sample_names)
                raise ValueError(f"Duplicate sample names in {fp}")

            return {x: IOReads(y) for x, y in zip(sample_names, r1)}

    def connect_one_to_one(
        self, iterator: AutobfxIterator, task_from: str, task_to: str
    ):
        for d in iterator:
            self.dag.add_edge(
                next(
                    n
                    for n in self.dag.nodes
                    if n.name == task_from
                    and all(n.id_dict[k] == v for k, v in d.items())
                ),
                next(
                    n
                    for n in self.dag.nodes
                    if n.name == task_to
                    and all(n.id_dict[k] == v for k, v in d.items())
                ),
            )

    def connect_one_to_many(
        self, iterator: AutobfxIterator, task_from: str, task_to: str
    ):
        for d in iterator:
            for n in self.dag.nodes:
                if n.name == task_to and all(n.id_dict[k] == v for k, v in d.items()):
                    self.dag.add_edge(
                        next(
                            n
                            for n in self.dag.nodes
                            if n.name == task_from
                            and all(n.id_dict[k] == v for k, v in d.items())
                        ),
                        n,
                    )

    def connect_many_to_one(
        self, iterator: AutobfxIterator, task_from: str, task_to: str
    ):
        for d in iterator:
            for n in self.dag.nodes:
                if n.name == task_from and all(n.id_dict[k] == v for k, v in d.items()):
                    self.dag.add_edge(
                        n,
                        next(
                            n
                            for n in self.dag.nodes
                            if n.name == task_to
                            and all(n.id_dict[k] == v for k, v in d.items())
                        ),
                    )

    def run(self):
        return self.flow()
