from datetime import datetime
from flask import Flask, jsonify, render_template, url_for, redirect, flash, session, request
import bcrypt
import database as dbase
from funciones import nocache, obtener_documentos_alumno, obtener_usuario_por_matricula, obtener_vinculacion
from create import init_create
from delete import init_delete
from update import init_update
from view import init_view
db = dbase.dbConnection()
app = Flask(__name__)
init_create(app)
init_delete(app)
init_update(app)
init_view(app)
app.secret_key = 'M0i1Xc$GfPw3Yz@2SbQ9lKpA5rJhDtE7'
app.config['SESSION_COOKIE_NAME'] = 'session_admin'

@app.route('/')
@nocache
def Index():
    
        return redirect(url_for('login'))


@app.route('/EduLink/Administradores/login/')
def login():
    return render_template('login.html')

@app.route("/EduLink/Vinculación/Periodos/")
@nocache
def iniciarPeriodo():
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})
        
        if administrador:
            conexion = db["Periodos"]
            Periodos = list(conexion.find({'Estatus': True}))
            return render_template("vinculacion/iniciarPeriodo.html", Periodos=Periodos)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    

    
@app.route('/iniciar/', methods=['POST'])
def iniciar():
    administracion = db['administradores']
    correo = request.form['correo']
    password = request.form['password']
    

    # Buscar en la colección de Administradores
    login_departamentos = administracion.find_one({'correo': correo})
    if login_departamentos and bcrypt.checkpw(password.encode('utf-8'), login_departamentos['contraseña']):
        session['correo'] = correo
        departamento = login_departamentos['departamento']
        administracion.update_one({"correo":correo}, 
            {'$set':{
                'en_linea': True, 'ultima_conexion': datetime.now()
            }})
        
        if departamento == 'vinculacion':
           return redirect(url_for('Home'))
        elif departamento == 'servicios_escolares':
            return redirect(url_for('servicios'))
        elif departamento == 'finanzas':
            return redirect(url_for('finanzas'))
        else:
            return redirect(url_for('login'))   

    # Si el inicio de sesión falla, muestra un mensaje de error
    flash('Correo o contraseña incorrectos', 'danger')
    return redirect(url_for('login'))

            


    
@app.route('/EduLink/Vinculación/Validar/Documentos_Alumno/<id_alumno>', methods=['GET', 'POST'])
def documentosAlumnos(id_alumno=None):
    if id_alumno is None:
        id_alumno = request.form.get('id_alumno')
        
    alumno = obtener_usuario_por_matricula(id_alumno)

    if alumno:
        documentos = obtener_documentos_alumno(id_alumno)
        if documentos:
            return render_template('vinculacion/documentosAlumnos.html', alumno=alumno, documentos=documentos)
        else:
            flash('Documentación de estadía sin asignar aun.', 'danger')
            return render_template('vinculacion/documentosAlumnos.html',alumno=alumno, documentos=documentos)
    else:
        flash('El alumno no está registrado.', 'danger')
        return redirect(url_for('ValidarAlum'))




@app.route("/EduLink/Vinculación/Validar/")
@nocache
def ValidarAlum():
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})
        if administrador:
            # Obtener la lista de carreras
            carreras = list(db['carreras'].find())
            periodos = list(db['Periodos'].find())
            
            # Convertir carreras y periodos a diccionarios con _id como clave
            carreras_dict = {str(carrera['_id']): carrera['NombreCarrera'] for carrera in carreras}
            periodos_dict = {str(periodo['_id']): {'NombrePeriodo': periodo['NombrePeriodo'], 'Duracion': periodo['Duracion']} for periodo in periodos}
            
            # Obtener la lista de alumnos
            alumnos = list(db['usuarios'].find())
            
            # Asignar el nombre de la carrera y del periodo a cada alumno
            for alumno in alumnos:
                alumno['NombreCarrera'] = carreras_dict.get(alumno['idCarrera'], 'Carrera no encontrada')
                periodo_info = periodos_dict.get(alumno.get('idPeriodo'), {'NombrePeriodo': 'Periodo no encontrado', 'Duracion': ''})
                alumno['NombrePeriodo'] = periodo_info['NombrePeriodo']
                alumno['Duracion'] = periodo_info['Duracion']
            
            return render_template("vinculacion/validarAlumno.html", Alumnos=alumnos, Carreras = carreras, Periodos=periodos)
        else:
         flash('Acceso denegado: No eres un administrador.', 'danger')
         return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    


@app.route("/EduLink/Vinculación/Carreras/")
@nocache
def Carrera():
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})  
        if administrador:  
            conexion = db['carreras']
            carreras = conexion.find()
            return render_template("vinculacion/agregarCarrera.html",carreras = carreras)
        else:
         flash('Acceso denegado: No eres un administrador.', 'danger')
         return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route("/EduLink/Vinculación/Archivos_Universidad/")
@nocache
def catalago():
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]
        periodos=db['Periodos'].find()
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})  
        if administrador:  
            

            return render_template("vinculacion/CargaAlumnos.html", Periodos=periodos)
        else:
         flash('Acceso denegado: No eres un administrador.', 'danger')
         return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route("/EduLink/Vinculación/administrar_Alumnos/")
@nocache
def Home():
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})  
        if administrador:     
            alumnos = db["Alumnos"]
            # Obtener la lista de Periodos
            periodos = list(db['Periodos'].find())
 
            # Convertir periodos a diccionarios con _id como clave
            periodos_dict = {str(periodo['_id']): {'Duracion': periodo['Duracion']} for periodo in periodos}
            # Obtener todos los alumnos
            lista_alumnos = list(alumnos.find({}))

            # Crear una lista para almacenar los alumnos con su progreso
            alumnos_con_progreso = []

            for alumno in lista_alumnos:
                periodo_info = periodos_dict.get(alumno.get('Periodo'), {'Duracion': ''})
                alumno['Duracion'] = periodo_info['Duracion']
                # Calcular el progreso y obtener la última actividad completada
                progreso, ultima_actividad = progreso_alumno(alumno["_id"])

                # Añadir el progreso y la última actividad al diccionario del alumno
                alumno["progreso"] = progreso
                alumno["ultima_actividad"] = ultima_actividad  # Añadir la última actividad

                # Agregar a la lista de resultados
                alumnos_con_progreso.append(alumno)

            return render_template("vinculacion/alumnos.html", alumnos=alumnos_con_progreso,periodos=periodos)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))




@app.route("/EduLink/Finanzas/")
def finanzas(): 
    if 'correo' in session:    
        correo_usuario = session['correo']
        administradores = db["administradores"]
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})  
        if administrador: 
            # Obtener la lista de carreras
            carreras = list(db['carreras'].find())
            periodos = list(db['Periodos'].find())
            
            # Convertir carreras y periodos a diccionarios con _id como clave
            carreras_dict = {str(carrera['_id']): carrera['NombreCarrera'] for carrera in carreras}
            periodos_dict = {str(periodo['_id']): {'Duracion': periodo['Duracion']} for periodo in periodos}
            
            # Obtener la lista de alumnos
            alumnos = list(db['usuarios'].find())
            
            # Asignar el nombre de la carrera y del periodo a cada alumno
            for alumno in alumnos:
                alumno['NombreCarrera'] = carreras_dict.get(alumno['idCarrera'], 'Carrera no encontrada')
                periodo_info = periodos_dict.get(alumno.get('idPeriodo'), {'NombrePeriodo': 'Periodo no encontrado', 'Duracion': ''})
                alumno['NombrePeriodo'] = periodo_info['NombrePeriodo']
                alumno['Duracion'] = periodo_info['Duracion']
            return render_template("Finanzas/finanza.html", Alumnos=alumnos, Carreras=carreras, Periodos=periodos)
        else:
         flash('Acceso denegado: No eres un administrador.', 'danger')
         return redirect(url_for('login'))
    else:
        return redirect (url_for('login'))

@app.route("/EduLink/Servicios/")
def servicios(): 
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})  
        if administrador: 
         # Obtener la lista de carreras
            carreras = list(db['carreras'].find())
            periodos = list(db['Periodos'].find())
            
            # Convertir carreras y periodos a diccionarios con _id como clave
            carreras_dict = {str(carrera['_id']): carrera['NombreCarrera'] for carrera in carreras}
            periodos_dict = {str(periodo['_id']): {'NombrePeriodo': periodo['NombrePeriodo'], 'Duracion': periodo['Duracion']} for periodo in periodos}
            
            # Obtener la lista de alumnos
            alumnos = list(db['usuarios'].find())
            
            # Asignar el nombre de la carrera y del periodo a cada alumno
            for alumno in alumnos:
                alumno['NombreCarrera'] = carreras_dict.get(alumno['idCarrera'], 'Carrera no encontrada')
                periodo_info = periodos_dict.get(alumno.get('idPeriodo'), {'NombrePeriodo': 'Periodo no encontrado', 'Duracion': ''})
                alumno['NombrePeriodo'] = periodo_info['NombrePeriodo']
                alumno['Duracion'] = periodo_info['Duracion']

            return render_template("Servicios/servicios.html", Alumnos=alumnos, Carreras=carreras, Periodos=periodos)
        else:
         flash('Acceso denegado: No eres un administrador.', 'danger')
         return redirect(url_for('login'))
    else:
        return redirect (url_for('login'))


def progreso_alumno(id_alumno):
    Alumnos_Act = db["Alumnos_Actividades"]
    Actividades = db["Actividades"]

    # Obtener todas las actividades desde la colección `Actividades` y ordenarlas por el campo `orden`
    lista_actividades = list(Actividades.find({}).sort("orden", 1))

    # Obtener las IDs de las actividades en el orden correcto
    actividades_ordenadas = [actividad["_id"] for actividad in lista_actividades]

    # Obtener todas las actividades del alumno
    actividades_alumno = list(Alumnos_Act.find({"idAlumno": id_alumno}))

    # Ordenar las actividades del alumno usando el orden de `actividades_ordenadas`
    actividades_alumno.sort(key=lambda x: actividades_ordenadas.index(x["idActividad"]))

    # Contadores
    total_actividades = len(actividades_alumno)
    completadas = 0
    ultima_actividad = None  # Variable para guardar el nombre de la última actividad completada

    # Revisar actividades en orden y contar cuántas están completadas
    for actividad in actividades_alumno:
        if actividad["estatus"] == "completado":
            completadas += 1
            # Obtener el nombre de la actividad correspondiente
            actividad_info = Actividades.find_one({"_id": actividad["idActividad"]})  # Corrección aquí
            if actividad_info:
                ultima_actividad = actividad_info["Actividad"]  # Guarda solo el nombre        
        else:
            # Tan pronto como encuentres una actividad no completada, para el conteo
            break

    # Calcular el porcentaje de progreso
    if total_actividades > 0:
        progreso = (completadas / total_actividades) * 100
    else:
        progreso = 0

    return progreso, ultima_actividad  # Devuelve el progreso y el nombre de la última actividad completada





########LOGOUT############

@app.route('/logout')
@nocache
def logout():
    correo = session.get('correo')
    if correo:
        administracion = db['administradores']
        administracion.update_one(
            {"correo": correo}, 
            {'$set': {'en_linea': False}}
        )
    
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('login'))  # Redirige al inicio de sesión



@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':

    app.run(debug=True,host='0.0.0.0', port=1000)
