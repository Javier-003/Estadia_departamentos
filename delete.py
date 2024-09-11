
from bson import ObjectId
from flask import flash, redirect, render_template, request, session, url_for
from funciones import eliminar_documento_alumno
import database as dbase
db = dbase.dbConnection()

def init_delete(app):

    @app.route('/eliminar_Alumno/<string:alumno_id>/')
    def eliminarAlumno(alumno_id):
        alumno = db['usuarios']
        alumno.delete_one({'_id':ObjectId(alumno_id)})
        eliminar_documento_alumno(alumno_id)
        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo}, 
                {'$set': {'ultimo_movimiento': 'Elimino a un alumno'}}
            )
        flash ('Alumno eliminado correctamente.','success')
        return redirect(url_for('administrarAlumno'))

    @app.route("/eliminar_Carrera/", methods=['POST'])
    def eliminarCarrera():
        carrera=db['carreras']
        carrera_id = request.form['idCarrera']
        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo}, 
                {'$set': {'ultimo_movimiento': 'Elimino una carrera'}}
            )
        carrera.delete_one({'_id':ObjectId(carrera_id)})
        return redirect(url_for('Carrera'))

    @app.route('/terminar_Periodo/', methods=['POST'])
    def terminarPeriodo():
        conexion = db['Periodos']
        periodo_id = request.form['idPeriodo']
        conexion.update_one({'_id': ObjectId(periodo_id)}, {'$set': {'Estatus': False}})
        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo}, 
                {'$set': {'ultimo_movimiento': 'Finalizo un periodo'}}
            )
        return redirect(url_for('iniciarPeriodo'))
    
    @app.route('/Eliminar_archivo/<archivo_id>/')
    def Eliminar_archivo(archivo_id):
        archivo = db['archivos_vinculacion']
        archivo.delete_one({'_id':ObjectId(archivo_id)})
        eliminar_documento_alumno(archivo_id)
        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo}, 
                {'$set': {'ultimo_movimiento': 'Elimino un documento'}}
            )
        flash ('Archivo eliminado correctamente.','success')
        return redirect(url_for('catalago'))