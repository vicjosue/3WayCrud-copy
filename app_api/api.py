from flask import Blueprint, request, jsonify, abort, url_for
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .modelsMSSQL import MSPelicula, MSReparto, MSActor, MSDirector, MSGenero, db as msDb
from .modelsMySQL import MyPelicula, MyReparto, MyActor, MyDirector, MyGenero, db as myDb
from .mongo import mongo

parent_app = None
api = Blueprint('api', __name__)
CORS(api)

# INSERTS CON POST
# UPDATES con PATCH
# DELETES con DELETE
# SELECT con GET


def jsonifyData(data):
    serialData = [e.serialize() for e in data]
    return jsonify(serialData)

# =====================
#        Actor
# =====================


@api.route('/actores')
def getActores():
    data = MSActor.query.all()
    return jsonifyData(data)


@api.route('/actor/<key>')
def getActorByKey(key):
    data = MSActor.query.filter_by(id=key)
    return jsonifyData(data)


@api.route('/actor', methods=['POST'])
def insertActor():
    try:
        msActor = MSActor(id=request.json.get('id', None), nombre=request.json.get(
            'nombre', None), pais=request.json.get('pais', None), nacimiento=request.json.get('nacimiento', None))
        msDb.session.add(msActor)
        # Send changes to DB to determine the id and maybe get integrity errors
        msDb.session.flush()
        myActor = MyActor(id=msActor.id, nombre=request.json.get('nombre', None), pais=request.json.get(
            'pais', None), nacimiento=request.json.get('nacimiento', None))
        myDb.session.add(myActor)
        mongo.db.ACTOR.insert_one({
            "_id": msActor.id,
            "nombre": request.json.get('nombre', None),
            "pais": request.json.get('pais', None),
            "nacimiento": request.json.get('nacimiento', None)
        })
    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'


@api.route('/actor/<key>', methods=['PATCH'])
def updateActorByKey(key):
    try:
        msDb.session.query(MSActor).filter(MSActor.id == key).update({
            MSActor.nombre: request.json.get('nombre', MSActor.nombre),
            MSActor.pais: request.json.get('pais', MSActor.pais),
            MSActor.nacimiento: request.json.get('nacimiento', MSActor.nacimiento)
        }, synchronize_session=False)

        myDb.session.query(MyActor).filter(MyActor.id == key).update({
            MyActor.nombre: request.json.get('nombre', MyActor.nombre),
            MyActor.pais: request.json.get('pais', MyActor.pais),
            MyActor.nacimiento: request.json.get('nacimiento', MyActor.nacimiento)
        }, synchronize_session=False)
        
        obj = mongo.db.ACTOR.find_one({"_id": eval(key)})
        mongo.db.ACTOR.update_one({"_id": eval(key)},{"$set": { "nombre": request.json.get('nombre', obj["nombre"]),
                                                                "pais": request.json.get('pais', obj["pais"]),
                                                                "nacimiento": request.json.get('nacimiento', obj["nacimiento"])}})
        mongo.db.PELICULA.update_many({"reparto.actor._id": eval(key)},{"$set": {"reparto.$.actor" : mongo.db.ACTOR.find_one({"_id": eval(key)}) }})

    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'


@api.route('/actor/<key>', methods=['DELETE'])
def deleteActorByKey(key):
    try:
        msActor = MSActor.query.filter_by(id=key).one()
        myActor = MyActor.query.filter_by(id=key).one()
        msDb.session.delete(msActor)
        myDb.session.delete(myActor)
        mongo.db.ACTOR.delete_one({"_id": eval(key)})
        mongo.db.PELICULA.update_many({},{ "$pull": { "reparto" : { "actor._id": eval(key)} } })
    except NoResultFound:
        abort(404)
        return
    except IntegrityError:
        return "integrity error", 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'

# =====================
#        Director
# =====================


@api.route('/director', methods=['POST'])
def insertDirector():
    try:
        msDirector = MSDirector(id=request.json.get('id', None), nombre=request.json.get(
            'nombre', None), pais=request.json.get('pais', None))
        msDb.session.add(msDirector)
        # Send changes to DB to determine the id and maybe get integrity errors
        msDb.session.flush()
        myDirector = MyDirector(id=msDirector.id, nombre=request.json.get(
            'nombre', None), pais=request.json.get('pais', None))
        myDb.session.add(myDirector)
        mongo.db.DIRECTOR.insert_one({
            "_id": msDirector.id,
            "nombre": request.json.get('nombre', None),
            "pais": request.json.get('pais', None)
        })
    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'

@api.route('/director/<key>', methods=['PATCH'])
def updateDirectorByKey(key):
    try:
        msDb.session.query(MSDirector).filter(MSDirector.id == key).update({
            MSDirector.nombre: request.json.get('nombre', MSDirector.nombre),
            MSDirector.pais: request.json.get('pais', MSDirector.pais)
        }, synchronize_session=False)

        myDb.session.query(MyDirector).filter(MyDirector.id == key).update({
            MyDirector.nombre: request.json.get('nombre', MyDirector.nombre),
            MyDirector.pais: request.json.get('pais', MyDirector.pais)
        }, synchronize_session=False)

        obj = mongo.db.DIRECTOR.find_one({"_id": eval(key)})
        mongo.db.DIRECTOR.update_one({"_id": eval(key)},{"$set":{"nombre": request.json.get('nombre', obj["nombre"]),
                                                                 "pais": request.json.get('pais', obj["pais"])}})
        mongo.db.PELICULA.update_many({"director._id": eval(key)},{"$set": {"director" : mongo.db.DIRECTOR.find_one({"_id": eval(key)}) }})

    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'

@api.route('/directores')
def getDirectores():
    data = MSDirector.query.all()
    return jsonifyData(data)


@api.route('/director/<key>', methods=['DELETE'])
def deleteDirectorByKey(key):
    try:
        msDirector = MSDirector.query.filter_by(id=key).one()
        myDirector = MyDirector.query.filter_by(id=key).one()
        msDb.session.delete(msDirector)
        myDb.session.delete(myDirector)
        mongo.db.DIRECTOR.delete_one({"_id": eval(key)})
        mongo.db.PELICULA.update_many({"director._id": eval(key)},{"$set": {"director" : None }})
    except NoResultFound:
        abort(404)
        return
    except IntegrityError:
        return "integrity error", 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'


# =====================
#        Genero
# =====================

@api.route('/genero', methods=['POST'])
def insertGenero():
    try:
        msGenero = MSGenero(id=request.json.get('id', None),
                            nombre=request.json.get('nombre', None))
        msDb.session.add(msGenero)
        # Send changes to DB to determine the id and maybe get integrity errors
        msDb.session.flush()
        myGenero = MyGenero(id=msGenero.id,
                            nombre=request.json.get('nombre', None))
        myDb.session.add(myGenero)
        mongo.db.GENERO.insert_one({
            "_id": msGenero.id,
            "nombre": request.json.get('nombre', None)
        })
    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'

@api.route('/genero/<key>', methods=['PATCH'])
def updateGeneroByKey(key):
    try:
        msDb.session.query(MSGenero).filter(MSGenero.id == key).update({
            MSGenero.nombre: request.json.get('nombre', MSGenero.nombre)
        }, synchronize_session=False)

        myDb.session.query(MyGenero).filter(MyGenero.id == key).update({
            MyGenero.nombre: request.json.get('nombre', MyGenero.nombre)
        }, synchronize_session=False)

        obj = mongo.db.GENERO.find_one({"_id": eval(key)})
        mongo.db.GENERO.update_one({"_id": eval(key)},{"$set":{"nombre": request.json.get('nombre', obj["nombre"])}})
        mongo.db.PELICULA.update_many({"genero._id": eval(key)},{"$set": {"genero" : mongo.db.GENERO.find_one({"_id": eval(key)}) }})

    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'

@api.route('/generos')
def getGeneros():
    data = MSGenero.query.all()
    return jsonifyData(data)


@api.route('/genero/<key>', methods=['DELETE'])
def deleteGeneroByKey(key):
    try:
        msGenero = MSGenero.query.filter_by(id=key).one()
        myGenero = MyGenero.query.filter_by(id=key).one()
        msDb.session.delete(msGenero)
        myDb.session.delete(myGenero)
        mongo.db.GENERO.delete_one({"_id": eval(key)})
        mongo.db.PELICULA.update_many({"genero._id": eval(key)},{"$set": {"genero" : None }})
    except NoResultFound:
        abort(404)
        return
    except IntegrityError:
        return "integrity error", 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'


# =====================
#        Pelicula
# =====================

@api.route('/pelicula', methods=['POST'])
def insertPelicula():
    try:
        msPelicula = MSPelicula(id=request.json.get('id', None), nombre=request.json.get('nombre', None), genero=request.json.get(
            'genero', None), director=request.json.get('director', None), ano=request.json.get('ano', None), calificacion=request.json.get('calificacion', None))
        msDb.session.add(msPelicula)
        # Send changes to DB to determine the id and maybe get integrity errors
        msDb.session.flush()
        myPelicula = MyPelicula(id=msPelicula.id, nombre=request.json.get('nombre', None), genero=request.json.get(
            'genero', None), director=request.json.get('director', None), ano=request.json.get('ano', None), calificacion=request.json.get('calificacion', None))
        myDb.session.add(myPelicula)
        mongo.db.PELICULA.insert_one({
            "_id": msPelicula.id,
            "nombre": request.json.get('nombre', None),
            "calificacion": request.json.get('calificacion', None),
            "ano": request.json.get('ano', None),
            "reparto": [],
            "director": mongo.db.DIRECTOR.find_one({"_id":request.json.get('director', None)}),
            "genero": mongo.db.GENERO.find_one({"_id":request.json.get('genero', None)})
        })
    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'

@api.route('/pelicula/<key>', methods=['PATCH'])
def updatePeliculaByKey(key):
    try:
        msDb.session.query(MSPelicula).filter(MSPelicula.id == key).update({
            MSPelicula.nombre: request.json.get('nombre', MSPelicula.nombre),
            MSPelicula.genero: request.json.get('genero', MSPelicula.genero),
            MSPelicula.director: request.json.get('director', MSPelicula.director),
            MSPelicula.ano: request.json.get('ano', MSPelicula.ano),
            MSPelicula.calificacion: request.json.get('calificacion', MSPelicula.calificacion),
        }, synchronize_session=False)
        
        myDb.session.query(MyPelicula).filter(MyPelicula.id == key).update({
            MyPelicula.nombre: request.json.get('nombre', MyPelicula.nombre),
            MyPelicula.genero: request.json.get('genero', MyPelicula.genero),
            MyPelicula.director: request.json.get('director', MyPelicula.director),
            MyPelicula.ano: request.json.get('ano', MyPelicula.ano),
            MyPelicula.calificacion: request.json.get('calificacion', MyPelicula.calificacion),
        }, synchronize_session=False)

        obj = mongo.db.PELICULA.find_one({"_id":eval(key)})
        mongo.db.PELICULA.update_one({"_id": eval(key)},{"$set":{"_id": request.json.get('_id', obj["_id"]),
                                                             "nombre": request.json.get('nombre', obj["nombre"]),
                                                             "calificacion": request.json.get('calificacion', obj["calificacion"]),
                                                             "ano": request.json.get('ano', obj["ano"])}})
        if obj["director"] != None:
            mongo.db.PELICULA.update_one({"_id": eval(key)},{"$set":
            {"director": mongo.db.DIRECTOR.find_one({"_id":request.json.get('director', obj["director"]["_id"])})}})
        else:
            mongo.db.PELICULA.update_one({"_id": eval(key)},{"$set":
            {"director": mongo.db.DIRECTOR.find_one({"_id":request.json.get('director', None)})}})
            
        if obj["genero"] != None:                          
            mongo.db.PELICULA.update_one({"_id": eval(key)},{"$set":
            {"genero": mongo.db.GENERO.find_one({"_id":request.json.get('genero', obj["genero"]["_id"])})}})            
        else:
            mongo.db.PELICULA.update_one({"_id": eval(key)},{"$set":
            {"genero": mongo.db.GENERO.find_one({"_id":request.json.get('genero', None)})}})


    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'



@api.route('/peliculas')
def getPeliculas():
    data = MSPelicula.query.all()
    return jsonifyData(data)


@api.route('/pelicula/<key>', methods=['DELETE'])
def deletePeliculaByKey(key):
    try:
        msPelicula = MSPelicula.query.filter_by(id=key).one()
        myPelicula = MyPelicula.query.filter_by(id=key).one()
        msDb.session.delete(msPelicula)
        myDb.session.delete(myPelicula)
        mongo.db.PELICULA.delete_one({"_id": eval(key)})
    except NoResultFound:
        abort(404)
        return
    except IntegrityError:
        return "integrity error", 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'


# =====================
#        Reparto
# =====================

@api.route('/reparto', methods=['POST'])
def insertReparto():
    try:
        msReparto = MSReparto(idPelicula=request.json.get('idPelicula'), idActor=request.json.get('idActor', None), personaje=request.json.get(
            'personaje', None), calificacion=request.json.get('calificacion', None))
        msDb.session.add(msReparto)
        # Send changes to DB to determine the id and maybe get integrity errors
        msDb.session.flush()
        myReparto = MyReparto(idPelicula=request.json.get('idPelicula'), idActor=request.json.get('idActor', None), personaje=request.json.get(
            'personaje', None), calificacion=request.json.get('calificacion', None))
        myDb.session.add(myReparto)
        mongo.db.PELICULA.update(
        { "_id": request.json.get('idPelicula') },
        { "$push": { "reparto": {"actor": mongo.db.ACTOR.find_one({"_id": request.json.get('idActor',None)}),
                                 "personaje":request.json.get('personaje', None),
                                 "calificacion": request.json.get('calificacion', None) }}})
    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'


@api.route('/repartos')
def getRepartos():
    data = MSReparto.query.all()
    return jsonifyData(data)

@api.route('/reparto/<keyPelicula>/<keyActor>', methods=['PATCH'])
def updateRepartoByKey(keyPelicula, keyActor):
    if (request.json.get('idPelicula', None) != None or request.json.get('idActor', None) != None):
        return 'can\'t change the keys', 400
    try:
        msDb.session.query(MSReparto).filter(MSReparto.idPelicula == keyPelicula,MSReparto.idActor == keyActor, ).update({
            MSReparto.personaje: request.json.get('personaje', MSReparto.personaje),
            MSReparto.calificacion: request.json.get('calificacion', MSReparto.calificacion)
        }, synchronize_session=False)
        
        myDb.session.query(MyReparto).filter(MyReparto.idPelicula == keyPelicula,MyReparto.idActor == keyActor, ).update({
            MyReparto.personaje: request.json.get('personaje', MyReparto.personaje),
            MyReparto.calificacion: request.json.get('calificacion', MyReparto.calificacion)
        }, synchronize_session=False)
        obj = mongo.db.PELICULA.find_one({"_id": int(keyPelicula), "reparto.actor._id": int(keyActor)},
                                     {"_id":0, "reparto.calificacion":1, "reparto.personaje":1})["reparto"][0]
        mongo.db.PELICULA.update({ "_id": int(keyPelicula) , "reparto.actor._id": int(keyActor)},
                                     { "$set": {"reparto.$.calificacion":request.json.get('calificacion',obj["calificacion"]),
                                                "reparto.$.personaje":   request.json.get('personaje',obj["personaje"])}})
    except IntegrityError:
        return 'integrity error', 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'

@api.route('/reparto/<keyPelicula>/<keyActor>', methods=['DELETE'])
def deleteRepartoByKey(keyPelicula, keyActor):
    try:
        msReparto = MSReparto.query.filter_by(
            idPelicula=keyPelicula, idActor=keyActor).one()
        myReparto = MyReparto.query.filter_by(
            idPelicula=keyPelicula, idActor=keyActor).one()
        msDb.session.delete(msReparto)
        myDb.session.delete(myReparto)
        mongo.db.PELICULA.update(
            { "_id": int(keyPelicula)},
            { "$pull": { "reparto": {"actor._id" :int(keyActor)}}})
    except NoResultFound:
        abort(404)
        return
    except IntegrityError:
        return "integrity error", 400
    msDb.session.commit()
    myDb.session.commit()
    return 'ok'



def init_app(app, url_prefix='/api/v1'):
    global parent_app
    parent_app = app
    app.register_blueprint(api, url_prefix=url_prefix)
