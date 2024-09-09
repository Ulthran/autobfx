from prefect import task


@task
def heyfastq():
    print("Hey, FastQ!")
    return "heyfastq"
