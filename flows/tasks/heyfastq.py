from prefect import task


@task
def run_heyfastq():
    print("Hey, FastQ!")
    return "heyfastq"
