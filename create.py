
import bcrypt
from bson import ObjectId
from flask import flash, redirect, render_template, request, session, url_for
from funciones import nocache
import database as dbase
db = dbase.dbConnection()
def init_create(app):

    @app.route("/agregar_Alumno/", methods=['POST'])
    def agregarAlumno():
        alumnos = db["usuarios"]
        if request.method == 'POST':
            correo = request.form['correoAlumn']
            matricula = request.form['matricula_Alum']
            existing_alumno = alumnos.find_one({
                '$or': [
                    {'correoAlumno': correo},
                    {'matricula': matricula}
                ]
            })
            if existing_alumno:
                flash ('El correo o la matrícula ya están registrados.','warning')
                return redirect(url_for('administrarAlumno'))
            correo = session.get('correo')
            if correo:
                administracion = db['administradores']
                administracion.update_one(
                    {"correo": correo}, 
                    {'$set': {'ultimo_movimiento': 'Asigno tipo de estadìa a alumno'}}
                )
            nombre = request.form['Nombre_Alumn']
            apellidos = request.form['apellidos_Alum']
            carrera = request.form['idCarrera']
            estadia = request.form['estadia']
            periodo = request.form['idPeriodo']
            grupo = request.form['grupo']
            telefono =request.form['telefonoAlumno']
            password = request.form['contraseñaAlumn']
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            alumnos.insert_one({
                'nombreAlumno': nombre,
                'telefonoAlumno':telefono,
                'apellidosAlumno': apellidos,
                'grupo': grupo ,
                'matricula': matricula,
                'correoAlumno': correo,
                'contraseñaAlumno': hashpass,
                'idCarrera': carrera,
                'estadiaAlumno': estadia,
                'idPeriodo': periodo,
                "tipo_estadia":'no asignado',
                "estatus_servicios": 'no asignado',
                "estatus_finanzas": 'no asignado',
                "folio_finanzas":'no asignado',
                "seguimiento_estadia":'no asignado',
                "formato_tres_opciones": {"estado": "activo", "archivo": None, "comentario": None}
            })
            flash ('Alumno registrado exitosamente.','success')
            return redirect(url_for('administrarAlumno'))
        else:
            flash ('El alumno no se pudo registrar.','danger')
        return redirect(url_for('administrarAlumno'))


    @app.route("/Registrarse/", methods=['POST'])
    def Registrarse():
        alumnos = db["usuarios"]
        if request.method == 'POST':
            correo = request.form['correoAlumn']
            matricula = request.form['matricula_Alum']
            existing_alumno = alumnos.find_one({
                '$or': [
                    {'correoAlumno': correo},
                    {'matricula': matricula}
                ]
            })
            if existing_alumno:
                flash ('El correo o la matrícula ya están registrados.','warning')
                return redirect(url_for('administrarAlumno'))

            nombre = request.form['Nombre_Alumn']
            apellidos = request.form['apellidos_Alum']
            carrera = request.form['idCarrera']
            estadia = request.form['estadia']
            periodo = request.form['idPeriodo']
            grupo = request.form['grupo']
            telefono =request.form['telefonoAlumno']
            password = request.form['contraseñaAlumn']
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            alumnos.insert_one({
                'nombreAlumno': nombre,
                'telefonoAlumno':telefono,
                'apellidosAlumno': apellidos,
                'grupo': grupo ,
                'matricula': matricula,
                'correoAlumno': correo,
                'contraseñaAlumno': hashpass,
                'idCarrera': carrera,
                'estadiaAlumno': estadia,
                'idPeriodo': periodo,
                "tipo_estadia":'no asignado',
                "estatus_servicios": 'no asignado',
                "estatus_finanzas": 'no asignado',
                "folio_finanzas":'no asignado',
                "seguimiento_estadia":'no asignado',
                "formato_tres_opciones": {"estado": "activo", "archivo": None, "comentario": None}
            })
            flash ('Alumno registrado exitosamente.','success')
            return redirect(url_for('login'))
        else:
            flash ('El alumno no se pudo registrar.','danger')
        return redirect(url_for('registro'))

    @app.route('/asignar_tipo_estadia/', methods=['POST'])
    @nocache
    def asignartipoestadia():
        id_alumno = request.form.get('idAlumno')
        estadia_Alumno = request.form.get('estadiaAlumno')
        nombre = request.form.get('nombreAlumno')
        tipo_estadia = request.form.get('tipo_estadia')
        alumno = db['usuarios'].find_one({'_id': ObjectId(id_alumno)})

        if alumno is None:
            flash('El alumno no está registrado', 'danger')
            return redirect(url_for('administrarAlumno'))
        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo}, 
                {'$set': {'ultimo_movimiento': 'Asigno tipo de estadìa a alumno'}}
            )

        if tipo_estadia == 'documentos_Especiales':
            documentos_Especiales_data = {
                "id_usuario": id_alumno,
                "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
                "kardex": {"estado": "activo", "archivo": None, "comentario": None},
                "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None, "comentario": None},
                "oficio_tutor_autorizando_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
                "registro_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
                "cronograma_de_actividades": {"estado": "desactivado", "archivo": None, "comentario": None},
                "1er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
                "2do_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
                "3er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
                "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None, "comentario": None}
            }

            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        "tipo_estadia":'Especial',
                    }
                }
            )

            db['documentos_especiales'].insert_one(documentos_Especiales_data)
            flash(f'Se le asignó la estadía Especial a {nombre} exitosamente', 'success')
            return redirect(url_for('administrarAlumno'))
        
        elif tipo_estadia == 'documentos_Foraneas':
            documentos_Foraneas_data = {
                "id_usuario": id_alumno,
                "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
                "kardex": {"estado": "activo", "archivo": None, "comentario": None},
                "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_de_buena_conducta": {"estado": "desactivado", "archivo": None,"comentario":None},
                "kardex_actualizado": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_compromiso_firmada": {"estado": "desactivado", "archivo": None,"comentario":None},
                "acuse_solicitud_de_espacio": {"estado": "desactivado", "archivo": None,"comentario":None},
                "acuse_carta_presentación": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_aceptación": {"estado": "desactivado", "archivo": None,"comentario":None},
                "registro_estadía": {"estado": "desactivado", "archivo": None,"comentario":None},
                "cronograma_de_actividades": {"estado": "desactivado", "archivo": None,"comentario":None},
                "1er_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "2do_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "3er_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "evaluación de estadía por empresa": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None,"comentario":None}
            }

            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        "tipo_estadia":'Foránea',
                    }
                }
            )

            db['documentos_foraneas'].insert_one(documentos_Foraneas_data)
            flash(f'Se le asignó la estadía Foránea a {nombre} exitosamente', 'success')
            return redirect(url_for('administrarAlumno'))
        
        elif estadia_Alumno == 'T.S.U' and tipo_estadia == 'documentosTSU':
            documentosTSU_data = {
                "id_usuario": id_alumno,
                "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
                "kardex": {"estado": "activo", "archivo": None, "comentario": None},
                "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None,"comentario":None},
                "copia_carnet": {"estado": "desactivado", "archivo": None,"comentario":None},
                "vigencia_seguro_social": {"estado": "desactivado", "archivo": None,"comentario":None},
                "acuse_solicitud_de_espacio": {"estado": "desactivado", "archivo": None,"comentario":None},
                "acuse_carta_presentación": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_aceptación": {"estado": "desactivado", "archivo": None,"comentario":None},
                "registro_estadía": {"estado": "desactivado", "archivo": None,"comentario":None},
                "cronograma_de_actividades": {"estado": "desactivado", "archivo": None,"comentario":None},
                "1er_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "2do_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "3er_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "evaluación_de_estadía_por_empresa": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_de_liberación_por_empresa": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None,"comentario":None}
            }

            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        "tipo_estadia":'TSU',
                    }
                }
            )

            db['documentos_TSU'].insert_one(documentosTSU_data)
            flash(f'Se le asignó la estadía Normal en TSU a {nombre} exitosamente', 'success')
            return redirect(url_for('administrarAlumno'))
        
        else:
            documentosLIC_ING_data = {
                "id_usuario": id_alumno,
                "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
                "kardex": {"estado": "activo", "archivo": None, "comentario": None},
                "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None,"comentario":None},
                "acuse_solicitud_de_espacio": {"estado": "desactivado", "archivo": None,"comentario":None},
                "acuse_carta_presentación": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_aceptación": {"estado": "desactivado", "archivo": None,"comentario":None},
                "registro_estadía": {"estado": "desactivado", "archivo": None,"comentario":None},
                "cronograma_de_actividades": {"estado": "desactivado", "archivo": None,"comentario":None},
                "1er_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "2do_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "3er_informe": {"estado": "desactivado", "archivo": None,"comentario":None},
                "evaluación_de_estadía_por_empresa": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta de liberación por empresa": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None,"comentario":None},
                "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None,"comentario":None}
            }

            db['usuarios'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        "tipo_estadia":'LIC.ING.',
                    }
                }
            )

            db['documentos_LIC_ING'].insert_one(documentosLIC_ING_data)
            flash(f'Se le asignó la estadía Normal en LIC.ING. a {nombre} exitosamente', 'success')
            return redirect(url_for('administrarAlumno'))


    @app.route("/agregar_Priodo/",methods=['POST'])
    @nocache
    def agregarPeriodo():
        conexion = db["Periodos"]
        nombre_periodo = request.form["N_periodo"]
        duración = request.form["periodo"]
        Status = True
        estatus_existente = conexion.count_documents({'Estatus' : Status})

        if estatus_existente < 2:
            correo = session.get('correo')
            if correo:
                administracion = db['administradores']
                administracion.update_one(
                    {"correo": correo}, 
                    {'$set': {'ultimo_movimiento': 'Agrego un periodo'}}
                )
            conexion.insert_one({
                'NombrePeriodo': nombre_periodo,
                'Duracion': duración,
                'Estatus': Status
                })
            flash ('Periodo creado correctamente','success')
            return redirect(url_for("iniciarPeriodo"))
        else:

            flash ('Ya existe un periodo activo','danger')
            return redirect(url_for("iniciarPeriodo"))


    @app.route("/agregar_Carrera/", methods=['GET', 'POST'])
    def agregarCarrera():
        if request.method == 'POST':
            conexion = db['carreras']
            nombreCarrera = request.form['N_carrera']
            abreviatura = request.form['Abreviatura']


            carrera_existente = conexion.find_one({'NombreCarrera': nombreCarrera})

            if carrera_existente is None:
                correo = session.get('correo')
                if correo:
                    administracion = db['administradores']
                    administracion.update_one(
                        {"correo": correo}, 
                        {'$set': {'ultimo_movimiento': 'Agrego una carrera'}}
                    )
                conexion.insert_one({
                    'NombreCarrera': nombreCarrera,
                    'Abreviatura': abreviatura,
                })
                flash('Carrera agregada correctamente', 'success')
                return redirect(url_for('Carrera'))
            
            flash('Carrera ya existente', 'danger')
        return redirect(url_for('Carrera'))

