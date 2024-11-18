from prefect import flow, task
from prefect.states import Failed
from prefect.task_runners import ThreadPoolTaskRunner
from time import sleep


@task
def logo_task(t: int, f: bool = False):
    sleep(t)

    if f:
        return Failed()


@flow(name="logo", log_prints=True, task_runner=ThreadPoolTaskRunner(max_workers=16))
def logo_flow(config: dict):
    print("This flow should write out 'BFX' with tasks and do nothing else.")

    # B
    b1 = logo_task.submit(2)
    sleep(0.1)
    logo_task.submit(0.5)
    logo_task.submit(0.5)
    logo_task.submit(0.5)
    logo_task.submit(0.5)
    sleep(0.1)
    b2 = logo_task.submit(2)
    sleep(0.1)
    logo_task.submit(0.5)
    logo_task.submit(0.5)
    logo_task.submit(0.5)
    logo_task.submit(0.5)
    sleep(0.1)
    b3 = logo_task.submit(2)
    sleep(1.25)

    b4 = logo_task.submit(0.5)
    b5 = logo_task.submit(0.5)
    b6 = logo_task.submit(0.5)
    b7 = logo_task.submit(0.5)
    sleep(0.1)
    b8 = logo_task.submit(0.5)
    b9 = logo_task.submit(0.5)
    b10 = logo_task.submit(0.5)
    b11 = logo_task.submit(0.5)

    # F
    [s.result() for s in [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11]]
    sleep(0.1)
    f2 = logo_task.submit(2)
    sleep(0.1)
    logo_task.submit(0.5)  # , wait_for=[f1])
    logo_task.submit(0.5)  # , wait_for=[f1])
    logo_task.submit(0.5)  # , wait_for=[f1])
    sleep(0.1)
    f3 = logo_task.submit(1.5)  # , wait_for=[b1, b2, b3, b4, b5, b6, b7, b8, b9])
    sleep(0.1)
    logo_task.submit(0.5)  # , wait_for=[f1])
    logo_task.submit(0.5)  # , wait_for=[f1])
    logo_task.submit(0.5)  # , wait_for=[f1])
    sleep(0.1)
    f4 = logo_task.submit(0.5)  # , wait_for=[f1])
    f5 = logo_task.submit(0.5)
    f6 = logo_task.submit(0.5)

    # X
    [s.result() for s in [f2, f3]]
    sleep(0.1)

    x1 = logo_task.submit(1)
    sleep(0.1)
    x2 = logo_task.submit(1)
    sleep(0.1)
    x3 = logo_task.submit(1)
    sleep(0.1)
    x4 = logo_task.submit(1)
    sleep(0.1)
    x5 = logo_task.submit(1)
    sleep(0.1)
    x6 = logo_task.submit(1, wait_for=[f4, f5, f6])
    sleep(0.1)
    x7 = logo_task.submit(1)
    sleep(0.1)
    x8 = logo_task.submit(1)
    sleep(0.1)
    x9 = logo_task.submit(1)
    sleep(0.1)
    x10 = logo_task.submit(1)
    sleep(0.1)
    x11 = logo_task.submit(1)

    sleep(0.1)
    [s.result() for s in [x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11]]
    x12 = logo_task.submit(0.3, wait_for=[x5])
    x12.result()

    """
    x1 = logo_task.submit(0.5)
    sleep(0.1)
    x2f = logo_task.submit(0.1, f=True, allow_failure=True)
    x2 = logo_task.submit(0.4, wait_for=[x2f])
    sleep(0.1)
    x3f = logo_task.submit(0.2, f=True, allow_failure=True)
    x3 = logo_task.submit(0.3, wait_for=[x3f])
    sleep(0.1)
    x4f = logo_task.submit(0.3, f=True, allow_failure=True)
    x4 = logo_task.submit(0.2, wait_for=[x4f])
    sleep(0.1)
    x5f = logo_task.submit(0.4, f=True, allow_failure=True)
    x5 = logo_task.submit(0.1, wait_for=[x5f])
    sleep(0.1)
    x6f = logo_task.submit(0.5, f=True, allow_failure=True)
    sleep(0.1)
    x7f = logo_task.submit(0.4, f=True, allow_failure=True)
    x7 = logo_task.submit(0.1, wait_for=[x7f])
    sleep(0.1)
    x8f = logo_task.submit(0.3, f=True, allow_failure=True)
    x8 = logo_task.submit(0.2, wait_for=[x8f])
    sleep(0.1)
    x9f = logo_task.submit(0.2, f=True, allow_failure=True)
    x9 = logo_task.submit(0.3, wait_for=[x9f])
    sleep(0.1)
    x10f = logo_task.submit(0.1, f=True, allow_failure=True)
    x10 = logo_task.submit(0.4, wait_for=[x10f])
    sleep(0.1)
    x11 = logo_task.submit(0.5)
    

    sleep(0.5)

    #x12f = logo_task.submit(0.5)
    """

    return "BFX"
