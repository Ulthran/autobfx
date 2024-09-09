from prefect import task


@task
def trimmomatic():
    print("Running Trimmomatic")
    return "trimmomatic"
