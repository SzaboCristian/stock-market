import logging
import os
from threading import Thread

from webserver.daemons.stock_prices_daemon import stock_prices_updater_task
from webserver.server import flask_app

if __name__ == "__main__":
    webserver_logger = logging.getLogger("webserver.error")
    flask_app.logger.handlers = webserver_logger.handlers
    flask_app.logger.setLevel(webserver_logger.level)

    # create crcrc inserter polling thread
    stock_prices_updater_thread = Thread(target=stock_prices_updater_task)
    stock_prices_updater_thread.setDaemon(True)
    stock_prices_updater_thread.start()

    flask_app.run(threaded=True, debug=(os.getenv("DEPLOYED") == "False"), host="0.0.0.0", port=5000)
