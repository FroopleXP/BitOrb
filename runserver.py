#!/usr/bin/env python
from bitorb import app
from bitorb.config import config
app.run(config["server"]["address"], config["server"]["port"])
