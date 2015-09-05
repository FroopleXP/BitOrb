#!/usr/bin/env python
from bitorb import app
from bitorb.config import config
from ssl import SSLContext
import threading
import time
from threading import Thread


# Pypy compatability
try:
    from ssl import PROTOCOL_TLSv1_2 as PROTOCOL_TLSv1
except ImportError:
    from ssl import PROTOCOL_TLSv1 as PROTOCOL_TLSv1

run_http = config["insecure"]["enabled"]
run_https = config["secure"]["enabled"]

if run_https:
    context = SSLContext(PROTOCOL_TLSv1)
    context.load_cert_chain(
        config["secure"]["cert"],
        config["secure"]["key"]
    )

if run_http and run_https:
    if config["debug"]:
        raise Warning("Cannot run in debug mode with both https and http enabled due to flask limitations.")
    Thread(
        target=app.run,
        kwargs={
            "host": config["server"]["address"],
            "port": config["secure"]["port"],
            "debug": config["debug"],
            "ssl_context": context
        }
    ).start()
    Thread(
        target=app.run,
        kwargs={
            "host": config["server"]["address"],
            "port": config["insecure"]["port"],
            "debug": config["debug"]
        }
    ).start()

elif run_http:
    app.run(
        host=config["server"]["address"],
        port=config["insecure"]["port"],
        debug=config["debug"]
    )

elif run_https:
    app.run(
        host=config["server"]["address"],
        port=config["insecure"]["port"],
        debug=config["debug"],
        ssl_context=context
    )

