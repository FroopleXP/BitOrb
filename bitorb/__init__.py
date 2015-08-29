from flask import Flask
from bitorb.config import config
app = Flask(__name__)
app.debug = True
app.secret_key = config["server"]["secret"]

import bitorb.api as api
import bitorb.main as main
import bitorb.database as database
import bitorb.helpers as helpers