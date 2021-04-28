from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MyActor(db.Model):
    __bind_key__ = 'mySQL'
    __tablename__ = 'ACTOR'
    id = db.Column('IdActor', db.Integer, nullable=False, primary_key=True, autoincrement=True)
    nombre = db.Column('Nombre', db.NCHAR(50))
    pais = db.Column('Pais', db.NCHAR(50))
    nacimiento = db.Column('Nacimiento', db.Integer)
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'pais': self.pais,
            'nacimiento': self.nacimiento
        }

class MyDirector(db.Model):
    __bind_key__ = 'mySQL'
    __tablename__ = 'DIRECTOR'
    id = db.Column('IdDirector', db.Integer, nullable=False, primary_key=True, autoincrement=True)
    nombre = db.Column('Nombre', db.Unicode(50))
    pais = db.Column('Pais', db.Unicode(50))
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'pais': self.pais
        }

class MyGenero(db.Model):
    __bind_key__ = 'mySQL'
    __tablename__ = 'GENERO'
    id = db.Column('IdGenero', db.Integer, nullable=False, primary_key=True, autoincrement=True)
    nombre = db.Column('Nombre', db.NCHAR(50), nullable=False)
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }

class MyPelicula(db.Model):
    __bind_key__ = 'mySQL'
    __tablename__ = 'PELICULA'
    id = db.Column('IdPelicula', db.Integer, nullable=False, primary_key=True, autoincrement=True)
    nombre = db.Column('Nombre', db.NCHAR(50))
    genero = db.Column('Genero', db.Integer, db.ForeignKey('GENERO.IdGenero', ondelete="SET NULL"))
    director = db.Column('Director', db.Integer, db.ForeignKey('DIRECTOR.IdDirector', ondelete="SET NULL"))
    ano = db.Column('A\xf1o', db.Integer)
    calificacion = db.Column('Calificacion', db.Integer)
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'genero': self.genero,
            'director': self.director,
            'ano': self.ano,
            'calificacion': self.calificacion
        }

class MyReparto(db.Model):
    __bind_key__ = 'mySQL'
    __tablename__ = 'REPARTO'
    idPelicula = db.Column(db.Integer, db.ForeignKey('PELICULA.IdPelicula', ondelete="CASCADE"), nullable=False, primary_key=True)
    idActor = db.Column(db.Integer, db.ForeignKey('ACTOR.IdActor', ondelete="CASCADE"), nullable=False, primary_key=True)
    personaje = db.Column('Personaje', db.NCHAR(50))
    calificacion = db.Column('Calificacion', db.Integer)
    def serialize(self):
        return {
            'idPelicula': self.idPelicula,
            'idActor': self.idActor,
            'personaje': self.personaje,
            'calificacion': self.calificacion
        }
    

def init_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)