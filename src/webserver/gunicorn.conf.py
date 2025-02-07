import multiprocessing
import os

# set bind address:port
from threading import Thread

from webserver.daemons.stock_prices_daemon import stock_prices_updater_task

ADDRESS = "0.0.0.0"
PORT = 8080
bind = f"{ADDRESS}:{PORT}"

# setup log level
loglevel = "debug" if os.getenv("DEPLOYED", False) is False else "info"

# setup gevent workers - 4 workers, 8 threads or less depending on cpu config
worker_class = "gevent"
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
threads = min(8, multiprocessing.cpu_count())
timeout = 10000
preload_app = True


def on_starting(server):
    # create and start stock prices updater thread - called before the master process is initialized
    # TODO - daemon bug - runs multiple times and takes too many resources, replace with cron outside ws
    # stock_prices_updater_thread = Thread(target=stock_prices_updater_task)
    # stock_prices_updater_thread.setDaemon(True)
    # stock_prices_updater_thread.start()
    pass


def worker_init(worker):
    # on SIGINT
    pass


def worker_exit(server, worker):
    # on SIGTERM
    pass
