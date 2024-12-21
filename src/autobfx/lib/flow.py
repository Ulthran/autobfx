import networkx as nx
from autobfx.lib.config import Config
from autobfx.lib.task import AutobfxTask
from prefect import flow


class AutobfxFlow:
    def __init__(self, config: Config, name: str, dag: nx.DiGraph):
        self.config = config
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

    def run(self):
        return self.flow()
