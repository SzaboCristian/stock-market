import logging
import os
from threading import Thread

from webserver.daemons.stock_prices_daemon import stock_prices_updater_task
from webserver.models.db import db
from webserver.server import flask_app

if __name__ == '__main__':
    # setup logger
    webserver_logger = logging.getLogger("webserver.error")
    flask_app.logger.handlers = webserver_logger.handlers
    flask_app.logger.setLevel(webserver_logger.level)

    # init users db
    db.app = flask_app
    db.init_app(flask_app)
    db.create_all()

    # create crcrc inserter polling thread
    stock_prices_updater_thread = Thread(target=stock_prices_updater_task)
    stock_prices_updater_thread.setDaemon(True)
    stock_prices_updater_thread.start()

    # run app
    flask_app.run(threaded=True, debug=(os.getenv("DEPLOYED") == "False"), host="0.0.0.0", port=5000)
