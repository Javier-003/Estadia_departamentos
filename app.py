from flask import Flask, render_template, url_for, redirect, flash, session, request
import bcrypt
import database as dbase
from funciones import nocache, obtener_departamento, obtener_documentos_alumno, obtener_usuario_por_matricula, obtener_vinculacion
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


@app.route('/')
@nocache
def Home():
    if 'correo' in session:
        correo = session['correo']
        usuario = obtener_vinculacion(correo)  
        if usuario:
            return render_template('vinculacion/main.html')
        else:
         return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route("/iniciar_Periodo/")
@nocache
def iniciarPeriodo():
    if 'correo' in session:    
        conexion =db["Periodos"]
        Periodos = list(conexion.find(({'Estatus': True})))
        return render_template("vinculacion/iniciarPeriodo.html", Periodos = Periodos)
    else:
       return redirect(url_for('login'))
    
@app.route('/iniciar/', methods=['POST'])
def iniciar():
    administracion = db['administradores']
    correo = request.form['correo']
    password = request.form['password']

    # Buscar en la colección de Administradores
    login_departamentos = administracion.find_one({'correo': correo})
    if login_departamentos and login_departamentos['contraseña'] == password:
        session['correo'] = correo
        departamento = login_departamentos['departamento']
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

            
        

    
@app.route('/Validar/documentos_Alumno/<id_alumno>', methods=['GET', 'POST'])
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




@app.route("/Validar/")
@nocache
def ValidarAlum():
    if 'correo' in session:
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
        return redirect(url_for('login'))
    


@app.route("/Carreras/")
@nocache
def Carrera():
    if 'correo' in session:    
        conexion = db['carreras']
        carreras = conexion.find()
        return render_template("vinculacion/agregarCarrera.html",carreras = carreras)
    else:
        return redirect(url_for('login'))

@app.route("/Catalago_De_Empresas/")
@nocache
def catalago():
    conexion = db['archivos_vinculacion']
    archivos = list(conexion.find())  # Convertir el cursor a una lista de documentos
    for archivo in archivos:
        archivo['extension'] = archivo['nombre'].split('.')[-1].lower()  # Obtener la extensión de cada archivo
    return render_template("vinculacion/catalogoDeEmpresas.html", archivos=archivos)

@app.route("/administrar_Alumnos/")
@nocache
def administrarAlumno():
    if 'correo' in session:
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
        
        return render_template("vinculacion/administrarAlumn.html", Alumnos=alumnos, Carreras=carreras, Periodos=periodos)
    else:
        return redirect(url_for('login'))



@app.route("/Finanzas/")
def finanzas(): 
    if 'correo' in session:    
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
        return render_template("Finanzas/finanza.html", Alumnos=alumnos, Carreras=carreras, Periodos=periodos)
    else:
        return redirect (url_for('login'))

@app.route("/Servicios/")
def servicios(): 
    if 'correo' in session:
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
        return redirect (url_for('login'))





########LOGOUT############

@app.route('/logout')
@nocache
def logout():
    session.clear()  #Elimina todas las variables de sesión
    return redirect(url_for('login'))  #Redirige al inicio de sesión



if __name__ == '__main__':

    app.run(debug=True)
