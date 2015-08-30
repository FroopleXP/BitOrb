from flask import Flask
import bitorb.config as config

app = Flask(__name__)
app.debug = True
app.secret_key = config.config["server"]["secret"]

import bitorb.api as api
import bitorb.database as database
import bitorb.errors as errors
import bitorb.helpers as helpers
import bitorb.handlers as handlers
import bitorb.main as main
import bitorb.template_helpers as template_helpers