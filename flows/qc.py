from prefect import flow
from tasks.fastqc import fastqc
from tasks.heyfastq import heyfastq
from tasks.trimmomatic import trimmomatic


@flow(name="qc", log_prints=True)
def qc():
    trimmomatic()
    heyfastq()
    fastqc()

    return "qc"
