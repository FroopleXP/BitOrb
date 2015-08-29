import json
import os

if os.path.exists("./config.json"):
    config = json.load(open("./config.json"))
else:
    config = json.load(open("./config.default.json"))
    json.dump(config, open("./config.json", "w"))
    print("Config file not found, creating...")

