__version__ = "0.0.0"
__author__ = "Charlie Bushman"
__email__ = "ctbushman@gmail.com"

from prefect.task_runners import ThreadPoolTaskRunner

thread_pool_task_runner = ThreadPoolTaskRunner(max_workers=3)
