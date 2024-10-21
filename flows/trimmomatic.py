from prefect import flow
from tasks.trimmomatic import run_trimmomatic


@flow(name="trimmomatic", log_prints=True)
def trimmomatic_flow():
    # Preprocess

    # Run
    run_trimmomatic()

    # Postprocess

    return "trimmomatic"
