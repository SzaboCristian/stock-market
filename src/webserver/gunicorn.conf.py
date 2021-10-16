import multiprocessing
import os

# set bind address:port
ADDRESS = "0.0.0.0"
PORT = 5000
bind = f"{ADDRESS}:{PORT}"

# setup log level
loglevel = "debug" if os.getenv("DEPLOYED", False) is False else "info"

# setup gevent workers - 4 workers, 8 threads or less depending on cpu config
worker_class = "gevent"
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
threads = min(8, multiprocessing.cpu_count())
timeout = 10000
preload_app = True


def worker_init(worker):
    # on SIGINT
    pass


def worker_exit(server, worker):
    # on SIGTERM
    pass
