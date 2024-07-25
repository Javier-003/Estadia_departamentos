import io
from bson import Binary, ObjectId
from flask import flash, redirect, request, session, url_for
from funciones import obtener_usuario_por_matricula, ver_documento_alumno_uta
import database as dbase
db = dbase.dbConnection()
from bson import ObjectId
from flask import send_file


def init_view(app):
    # Ruta para mostrar el PDF en una nueva ventana o modal
    @app.route('/alumno_UTA/ver/<nombre_archivo>/<id_alumno>', methods=['GET'])
    def ver_archivo_alumno_uta(nombre_archivo, id_alumno):
        alumno = obtener_usuario_por_matricula(id_alumno)
        if alumno:
            datos = ver_documento_alumno_uta(id_alumno, nombre_archivo)
            if datos:
                documento_stream = io.BytesIO(datos)
                documento_stream.seek(0)
                mimetype = 'application/pdf'
                return send_file(documento_stream, as_attachment=False, mimetype=mimetype)
        return 'Archivo no encontrado', 404


    @app.route('/Validar/documentos_Alumno/ver/<nombre_archivo>/<id_alumno>', methods=['GET'])
    def ver_archivo_alumno(nombre_archivo, id_alumno):
        alumno = obtener_usuario_por_matricula(id_alumno)
        if alumno:
            datos = ver_documento_alumno_uta(id_alumno, nombre_archivo)
            if datos:
                documento_stream = io.BytesIO(datos)
                documento_stream.seek(0)
                mimetype = 'application/pdf'
                return send_file(documento_stream, as_attachment=False, mimetype=mimetype)
        return 'Archivo no encontrado', 404

    @app.route('/Catalago_De_Empresas/upload/', methods=['POST'])
    def upload_file():
        conexion = db["archivos_vinculacion"]
        archivo = request.files['archivo']
        descripcion = request.form["descripcion"]

        if archivo:
            if archivo.filename.endswith('.pdf') or archivo.filename.endswith('.doc') or archivo.filename.endswith('.docx') or archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
                archivo_data = archivo.read()
                archivo_nombre = archivo.filename  # Guarda el nombre del archivo
                archivo_bin = Binary(archivo_data)  # Almacena el contenido del archivo como datos binarios en la base de datos
            else:
                flash('El archivo debe ser .pdf, .doc, .docx, .xlsx, .xls','warning')
                return redirect(url_for('registerColaborador'))
        else:
            archivo_nombre = None
            archivo_bin = None

        conexion.insert_one({
            'nombre': archivo_nombre,  # Guarda el nombre del archivo en la base de datos
            'archivo': archivo_bin,
            'descripcion': descripcion,
        })
        flash('Archivo guardado exitosamento','success')
        return redirect(url_for('catalago'))


    @app.route('/Catalago_De_Empresas/ver/<archivo_id>/', methods=['GET'])
    def ver_archivo(archivo_id):
        conexion = db["archivos_vinculacion"]
        archivo = conexion.find_one({'_id': ObjectId(archivo_id)})

        if archivo:
            nombre = archivo['nombre']
            datos = archivo['archivo']
            documento_stream = io.BytesIO(datos)
            documento_stream.seek(0)
            extension = nombre.split('.')[-1].lower()  # Obtener la extensión del archivo
            if extension == 'pdf':
                mimetype = 'application/pdf'
            elif extension in ['doc', 'docx']:
                mimetype = 'application/msword'
            elif extension in ['xls', 'xlsx']:
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                # Para otros tipos de archivos, establecer el tipo MIME como genérico
                mimetype = 'application/octet-stream'
            return send_file(documento_stream, as_attachment=False, mimetype=mimetype)
        else:
            return 'Archivo no encontrado', 404



    @app.route('/Catalago_De_Empresas/descargar/<archivo_id>/', methods=['GET'])
    def descargar_archivo(archivo_id):
        conexion = db["archivos_vinculacion"]
        archivo = conexion.find_one({'_id': ObjectId(archivo_id)})

        if archivo:
            datos = archivo['archivo']
            nombre = archivo['nombre']
            
            # Obtener la extensión del archivo
            extension = nombre.split('.')[-1].lower()
            
            # Determinar el tipo MIME según la extensión del archivo
            if extension == 'pdf':
                mimetype = 'application/pdf'
            elif extension in ['doc', 'docx']:
                mimetype = 'application/msword'
            elif extension in ['xls', 'xlsx']:
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                # Para otros tipos de archivos, establecer el tipo MIME como genérico
                mimetype = 'application/octet-stream'
            
            return send_file(io.BytesIO(datos), as_attachment=True, mimetype=mimetype, download_name=nombre)
        else:
            return 'Archivo no encontrado', 404
