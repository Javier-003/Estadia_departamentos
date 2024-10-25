from datetime import datetime
import io
import bcrypt
from bson import Binary, ObjectId
from flask import flash, redirect, render_template, request, session, url_for
from datetime import datetime
from funciones import obtener_usuario_por_matricula, ver_documento_alumno_uta
import database as dbase
db = dbase.dbConnection()
from bson import ObjectId
from flask import send_file
import pandas as pd

def init_view(app):
    # Ruta para mostrar el PDF en una nueva ventana o modal
    @app.route('/EduLink/Vinculación/Validar/ver/<nombre_archivo>/<id_alumno>', methods=['GET'])
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
    
    @app.route('/EduLink/Vinculación/Validar/Documentos_Alumno/ver/formato_tres_opciones/<id_alumno>', methods=['GET'])
    def ver_archivo_alumno_uta_1(id_alumno):
        

        try:
            id_alumno = ObjectId(id_alumno)
        except Exception as e:
            return 'ID de alumno inválido', 400

        # Busca el documento del alumno
        alumno_documento = db['usuarios'].find_one({'_id': id_alumno})
        

        if alumno_documento and 'formato_tres_opciones' in alumno_documento:
            formato_tres_opciones = alumno_documento['formato_tres_opciones']
            

            if formato_tres_opciones and 'archivo' in formato_tres_opciones:
                archivo = formato_tres_opciones['archivo']
                

                if archivo:
                    datos = archivo
                    documento_stream = io.BytesIO(datos)
                    documento_stream.seek(0)
                    mimetype = 'application/pdf'
                    return send_file(documento_stream, as_attachment=False, mimetype=mimetype)

        return 'Archivo no encontrado', 404

    @app.route('/EduLink/Vinculación/Validar/Documentos_Alumno/ver/<nombre_archivo>/<id_alumno>', methods=['GET'])
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
        archivo = request.files['archivo']
        alumno = db["Alumnos"]
        carga = db ["Carga_Alumnos"]
       
        Periodo = request.form.get('Periodo')
        TSU_ING = request.form.get('tsu_ing')
        fecha_carga = datetime.combine(datetime.now().date(), datetime.min.time())

        existe_carga = carga.find_one({'periodo': Periodo, 'TSU_ING': TSU_ING})
        if existe_carga:
                flash(f'Ya existe una carga de alumnos para el periodo "{Periodo}" y tipo "{TSU_ING}".', 'warning')
                return redirect(url_for('catalago'))
        else:
            archivo_data = archivo.read()
            archivo_bin = Binary(archivo_data)
            carga.insert_one({
                    'Archivo': archivo_bin,
                    'periodo':Periodo,
                    'TSU_ING':TSU_ING,
                    'Fecha_Carga':fecha_carga  # Almacena solo la fecha (YYYY-MM-DD)
                })
        if archivo:

            if archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
                # Leer el archivo Excel y seleccionar las columnas necesarias
                alumnos = pd.read_excel(archivo, usecols=['Nombre', 'Apellido_Pat', 'Apellido_Mat', 'Matricula','Correo_Institucional','Contraseña','Telefono','Carrera','Cuatrimestre','Grupo'])
                
                # Validar que no haya datos faltantes en las columnas requeridas
                if alumnos[['Nombre', 'Apellido_Pat', 'Apellido_Mat', 'Matricula','Correo_Institucional','Contraseña','Telefono','Carrera','Cuatrimestre','Grupo']].isnull().any().any():
                    flash('El archivo contiene filas con datos faltantes. Asegúrate de que todos los campos estén completos.', 'warning')
                    return redirect(url_for('catalago'))
                
                # Encriptar contraseñas y agregar las columnas adicionales
                for index, row in alumnos.iterrows():
                    # Encriptar la contraseña
                    password = row['Contraseña']
                    if password and isinstance(password, str):
                        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        alumnos.at[index, 'Contraseña'] = hashed_password.decode('utf-8')
                
                alumnos['Periodo'] = Periodo        
                alumnos['TSU/ING'] = TSU_ING
                
                # Convertir los datos a JSON para insertarlos en MongoDB
                data_json = alumnos.to_dict(orient='records')
                
                # Insertar los registros en la base de datos
                alumno.insert_many(data_json)
                

                # Llamar a la función para registrar actividades
                if asignar_actividades():
                    flash('Alumnos cargados exitosamente', 'success')
                else:
                    flash('Alumnos cargados, pero ocurrió un error al registrar actividades.', 'warning')
            else:
                flash('El archivo debe de ser .xlsx, .xls para poder ser compatible', 'warning')
                return redirect(url_for('administrarAlumno'))
        else:
            archivo = None

        return redirect(url_for('administrarAlumno'))
    
    

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
        
    


    def asignar_actividades():
    # Colecciones
        Actividades = db["Actividades"]
        Alumnos_Act = db["Alumnos_Actividades"]
        Alumnos = db["Alumnos"]

        lista_actividades = list(Actividades.find().sort("Orden", 1))  # Convertir a lista para evitar múltiples consultas

        # Obtener todos los IDs de los alumnos
        id_alumnos = [alumno["_id"] for alumno in Alumnos.find({}, {"_id": 1})]

        # Crear registros en Alumnos_Actividades para cada alumno y cada actividad
        for id_alumno in id_alumnos:
            alumno_actividades = []  # Crea un arreglo para las actividades del alumno
            for actividad in lista_actividades:
                # Verificar si la actividad es la de orden 1
                estatus = "completado" if actividad["Orden"] == 0 else "no iniciado"

                alumno_actividad = {
                    "idAlumno": id_alumno,
                    "idActividad": actividad["_id"],
                    "estatus": estatus  # Establecer el estatus según el orden de la actividad
                }
                alumno_actividades.append(alumno_actividad)  # Inserta en el arreglo alumno_actividad

            # Inserta las actividades a un alumno y regresa para seguir con otro alumno
            if alumno_actividades:
                Alumnos_Act.insert_many(alumno_actividades)

        return True
    



