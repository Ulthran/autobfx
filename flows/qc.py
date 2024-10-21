from prefect import flow
from flows.trimmomatic import trimmomatic_flow


@flow(name="qc", log_prints=True)
def qc():
    trimmomatic_flow()
    # heyfastq()
    # fastqc()

    return "qc"


if __name__ == "__main__":
    qc()
