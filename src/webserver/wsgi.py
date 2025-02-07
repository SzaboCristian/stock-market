from gevent import monkey

# monkey patch all standard libs
monkey.patch_all()

import logging
import os
from threading import Thread

from webserver.daemons.stock_prices_daemon import stock_prices_updater_task
from webserver.model.db import db
from webserver.server import flask_app

# setup logger
webserver_logger = logging.getLogger("webserver.error")
flask_app.logger.handlers = webserver_logger.handlers
flask_app.logger.setLevel(webserver_logger.level)

# init users db
db.app = flask_app
db.init_app(flask_app)
db.create_all()

if __name__ == "__main__":
    # create and start stock prices updater thread - only when run without gunicorn; thread started with gunicorn from
    # gunicorn.conf.py
    # TODO - daemon bug - runs multiple times and takes too many resources, replace with cron outside ws
    # stock_prices_updater_thread = Thread(target=stock_prices_updater_task)
    # stock_prices_updater_thread.setDaemon(True)
    # stock_prices_updater_thread.start()

    # run app - only when run without gunicorn
    flask_app.run(
        threaded=True,
        debug=(os.getenv("DEPLOYED") == "False"),
        host="0.0.0.0",
        port=8080,
    )
