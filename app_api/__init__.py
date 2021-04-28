from flask import Flask
app = Flask(__name__)
import app_api.config as config
app.config["SQLALCHEMY_DATABASE_URI"] = config.msSqlConn
app.config["SQLALCHEMY_BINDS"] = {
    'mySQL':config.mySqlConn
} 
app.config['MONGO_URI'] = config.mongoConn

import app_api.modelsMSSQL as modelsMSSQL
import app_api.modelsMySQL as modelsMySQL
import app_api.mongo as mongo
from .api import init_app
from .commands import init_app as init_commands
modelsMSSQL.init_app(app) # Init MS SQL
modelsMySQL.init_app(app) # Init My SQL
mongo.init_app(app) # Init Mongo
init_app(app) # Init API
init_commands(app) # Init flask commands

@app.route("/heartbeat")
def home():
    return "alive"

if __name__ == "__main__":
    app.run(debug=True)