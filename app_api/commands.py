from flask.cli import AppGroup
from .modelsMSSQL import db as msDb
from .modelsMySQL import db as myDb

apps = AppGroup('apps')

@apps.command('create-tables')
def createTables():
    msDb.create_all()
    myDb.create_all()

def init_app(app):
    app.cli.add_command(apps)