import bcrypt
from bson import  ObjectId
from flask import flash, redirect,  request, url_for
import database as dbase
from funciones import aceptar_documento, actualizar_estado_documento, subir_documento
db = dbase.dbConnection()
from bson import ObjectId


def init_update(app):


    @app.route("/editar_Alumnos/", methods=['POST'])
    def editarAlumno():
        id_alumno = request.form.get('idAlumno')
        Nombre = request.form['Nombre_Alumn']
        apellidos = request.form['apellidos_Alum']
        matricula = request.form['matricula_Alum']
        correo = request.form['correoAlumn']
        contraseña = request.form['contraseñaAlumn']
        carrera = request.form['idCarrera']
        estadia = request.form['estadia']
        hashpass = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

        alumno = db['usuarios'].find_one({'_id':ObjectId(id_alumno)})

        if alumno:
            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        'nombreAlumno':Nombre,
                        'apellidosAlumno' : apellidos,
                        'matricula' : matricula,
                        'correoAlumno' : correo,
                        'contraseñaAlumno' : hashpass,
                        'idCarrera' : carrera,
                        'estadiaAlumno' : estadia
                    }
                }
            )
            flash (f'Datos de {Nombre} actualizados exitosamente', 'success')
            return redirect(url_for('administrarAlumno'))
        else:
            flash('Alumno no encontrado en la base de datos','danger')
        return redirect(url_for('administrarAlumno'))



    @app.route('/actualizar_estado_documento/<id_alumno>/<documento_nombre>', methods=['GET', 'POST'])
    def actualizar_estado_documento_nuevo(id_alumno, documento_nombre):

        if actualizar_estado_documento(id_alumno, documento_nombre):
            flash('Estado del documento actualizado exitosamente.', 'success')
        else:
            flash('No se pudo actualizar el estado del documento.', 'danger')
        
        return redirect(url_for('documentosAlumnos', id_alumno=id_alumno))



    @app.route('/aceptar_documento/<id_alumno>/<documento_nombre>', methods=['GET', 'POST'])
    def aceptar_documento_nuevo(id_alumno, documento_nombre):
        
        if aceptar_documento(id_alumno, documento_nombre):
            flash('Documento aceptado exitosamente.', 'success')
        else:
            flash('No se pudo aceptar el documento intentelo de nuevo.', 'danger')
        
        return redirect(url_for('documentosAlumnos', id_alumno=id_alumno))


    def devolver_documento(id_alumno, documento_nombre, comentario):
        documentos_collections = ['documentos_TSU', 'documentos_LIC_ING', 'documentos_foraneas', 'documentos_especiales']
        for collection in documentos_collections:
            documento = db[collection].find_one({'id_usuario': id_alumno})
            if documento and documento_nombre in documento:
                db[collection].update_one(
                    {'id_usuario': id_alumno},
                    {'$set': {f'{documento_nombre}.estado': 'devuelto', f'{documento_nombre}.comentario': comentario}}
                )
                return True
        return False

    @app.route('/devolver_Documento/', methods=['POST'])
    def devolver_documento_alumno():
        id_alumno = request.form.get('id_alumno')
        documento_nombre = request.form.get('Nombre_documento')
        comentario = request.form['comentario']
        
        if devolver_documento(id_alumno, documento_nombre,comentario):
            flash('Documento devuelto exitosamente.', 'success')
        else:
            flash('No se pudo devolver el documento intentelo de nuevo.', 'danger')
        
        return redirect(url_for('documentosAlumnos', id_alumno=id_alumno))


    @app.route('/subir_documento/<id_alumno>/<documento_nombre>', methods=['GET', 'POST'])
    def subir_documento_alumno(id_alumno, documento_nombre):
        if request.method == 'POST':
            archivo = request.files['archivo']
            if subir_documento(id_alumno, documento_nombre, archivo):
                flash('Documento subido exitosamente.', 'success')
            else:
                flash('No se pudo subir el documento. Inténtelo de nuevo.', 'danger')
            return redirect(url_for('alumno_vista', id_alumno=id_alumno))
        return redirect(url_for('alumno_vista', id_alumno=id_alumno))

    @app.route("/acreditar_Alumno/<id_alumno>/", methods=['GET', 'POST'])
    def acreditar_Alumno(id_alumno):
        
        alumno = db['usuarios'].find_one({'_id':ObjectId(id_alumno)})

        if alumno:
            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        'estatus_servicios':'acreditado'
                    }
                }
            )
            
            return redirect(url_for('servicios'))
        else:
            flash('Alumno no encontrado en la base de datos','danger')
        return redirect(url_for('servicios'))

    @app.route("/no_acreditar_Alumno/<id_alumno>/", methods=['GET', 'POST'])
    def no_acreditar_Alumno(id_alumno):
        
        alumno = db['usuarios'].find_one({'_id':ObjectId(id_alumno)})

        if alumno:
            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        'estatus_servicios':'no acreditado'
                    }
                }
            )
            
            return redirect(url_for('servicios'))
        else:
            flash('Alumno no encontrado en la base de datos','danger')
        return redirect(url_for('servicios'))

    @app.route("/adeudo_Alumno/<id_alumno>/", methods=['GET', 'POST'])
    def adeudo_Alumno(id_alumno):
    
        alumno = db['usuarios'].find_one({'_id':ObjectId(id_alumno)})

        if alumno:
            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        'estatus_finanzas':'con adeudo'
                    }
                }
            )
            
            return redirect(url_for('finanzas'))
        else:
            flash('Alumno no encontrado en la base de datos','danger')
        return redirect(url_for('finanzas'))

    @app.route("/sin_adeudo_Alumno/", methods=['POST'])
    def sin_adeudo_Alumno():
        id_alumno = request.form.get('idAlumno')
        folio = request.form['folio']
        alumno = db['usuarios'].find_one({'_id':ObjectId(id_alumno)})

        if alumno: 
            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        'estatus_finanzas':'sin adeudo ',
                        'folio_finanzas': folio
                    }
                }
            )
            
            return redirect(url_for('finanzas'))
        else:
            flash('Alumno no encontrado en la base de datos','danger')
        return redirect(url_for('finanzas'))   