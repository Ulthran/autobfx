import networkx as nx
from autobfx.lib.config import Config
from autobfx.lib.iterator import AutobfxIterator
from autobfx.lib.task import AutobfxTask
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
    def empty_flow(cls, name: str) -> "AutobfxFlow":
        return cls(name, nx.DiGraph())

    @classmethod
    def compose_flows(cls, name: str, flows: list["AutobfxFlow"]) -> "AutobfxFlow":
        dag = nx.compose_all([flow.dag for flow in flows])
        return cls(name, dag)

    def connect_one_to_one(
        self, iterator: AutobfxIterator, task_from: str, task_to: str
    ):
        for k, _ in iterator:
            self.dag.add_edge(
                next(
                    (
                        n
                        for n in self.dag.nodes
                        if n.name == task_from and n.id_dict[iterator.name] == k
                    ),
                    None,
                ),
                next(
                    (
                        n
                        for n in self.dag.nodes
                        if n.name == task_to and n.id_dict[iterator.name] == k
                    ),
                    None,
                ),
            )

    def connect_one_to_many(
        self, iterator: AutobfxIterator, task_from: str, task_to: str
    ):
        for k, _ in iterator:
            for n in [
                n
                for n in self.dag.nodes
                if n.name == task_to and n.id_dict[iterator.name] == k
            ]:
                self.dag.add_edge(
                    next(
                        (
                            n
                            for n in self.dag.nodes
                            if n.name == task_from and n.id_dict[iterator.name] == k
                        ),
                        None,
                    ),
                    n,
                )

    def connect_many_to_one(
        self, iterator: AutobfxIterator, task_from: str, task_to: str
    ):
        for k, _ in iterator:
            for n in [
                n
                for n in self.dag.nodes
                if n.name == task_from and n.id_dict[iterator.name] == k
            ]:
                self.dag.add_edge(
                    n,
                    next(
                        (
                            n
                            for n in self.dag.nodes
                            if n.name == task_to and n.id_dict[iterator.name] == k
                        ),
                        None,
                    ),
                )

    def run(self):
        return self.flow()
