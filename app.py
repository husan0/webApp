from flask import Flask, render_template,request,redirect,flash,session
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename
import os


#configuracion de la apliacion

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'mi clave es secreta'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bd_proyecto'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'static/Uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

mysql.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#VIEWS -----------------------------------------------------------------

@app.route('/')
def main():
    if session.get('username'):
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/index')
def inicio():
    if session.get('username'):
        return render_template('index.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')

#-------------------------------PRODUCTOS-------------------------------
@app.route('/irBuscar')
def irBuscar():
    if session.get('username'):
        return render_template('producto/buscar.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')

@app.route('/irAgregar')
def irAgregar():
    if session.get('username'):
        return render_template('producto/agregar.html',lista = getTipoProducto(), listaC = getCategoria())
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')

@app.route('/irEliminar')
def irEliminar():
    if session.get('username'):
        return render_template('producto/eliminar.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')

@app.route('/irListar')
def irListar():
    if session.get('username'):
        return render_template('producto/listar.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')

@app.route('/irModificar')
def irModificar():
    if session.get('username'):
        return render_template('producto/modificar.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')
#-------------------------------USUARIOS-------------------------------
@app.route('/volver')
def volver():
    if session.get('username'):
        return render_template('index.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


@app.route('/respuesta')
def respuesta():
    if session.get('username'):
        return render_template('respuesta.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


@app.route('/desconectar')
def desconectar():
    session.pop('username',None)
    flash('Desconectado :(')
    return redirect('/')


#------------------------FUNCIONES PRODUCTO------------------------------

@app.route('/buscar',methods=['POST'])
def webBuscar():
    nombre_producto = request.form['nombre']
    data = buscarProducto(nombre_producto)
    if len(data) is 0:
        flash('no existen registros')
        return render_template('producto/buscar.html')
    else:
        return render_template('producto/buscar.html', id = data[0][0], nombre = data[0][1], stock = data[0][2], precio = data[0][3], tipo = data[0][10],categoria = data[0][13], detalle = data[0][6], imagen = os.path.join(app.config['UPLOAD_FOLDER'], data[0][7]))

@app.route('/buscarModificar',methods=['POST'])
def buscarModificar():
    nombre_producto = request.form['nombre']
    data = buscarProducto(nombre_producto)
    if len(data) is 0:
        flash('no existen registros')
        return render_template('producto/modificar.html')
    else:
        return render_template('producto/modificar.html', nombre = data[0][1], stock = data[0][2], precio = data[0][3], tipo = data[0][10],categoria = data[0][13], detalle = data[0][6], imagen = os.path.join(app.config['UPLOAD_FOLDER'], data[0][7]),tipo_producto=getTipoProducto(), categoria_producto= getCategoria())

@app.route('/agregar', methods=['GET','POST'])
def webAgregar():
    nombre_producto = request.form['nombre']    
    stock = request.form['stock']
    precio = request.form['price']
    tipo = request.form.get('tipoProducto')
    categoria = request.form.get('categoria')
    detalle = request.form['detalle']
    file = request.files['file']
    data = agregarProducto(nombre_producto,stock,precio,categoria,tipo,detalle,file)
    if len(data) is 0:
        flash('Agregado correctamente')
        return render_template('index.html')
    else:
        flash('No se puede agregar')
        return render_template('index.html')

@app.route('/login',methods=['POST'])
def webLogin():
    try:
        user_email = request.form['email']
        user_pass = request.form['password']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `usuario` WHERE `correo_usuario`= %(user)s and `contrasenia_usuario`= %(pass)s ',{'user':user_email,'pass':user_pass})
        data = cursor.fetchall()
        if len(data) is 1:
            session['username'] = data[0][1]
            flash('Bienvenido')
            return render_template('index.html')
        else:
            flash('Error usuario o contraseña incorrecto')
            return render_template('login.html')
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()
        

def buscarProducto(nombre_producto):
        try:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM producto INNER JOIN tipo_producto on producto.id_tipo_producto = tipo_producto.id_tipo_producto INNER JOIN categoria_producto on producto.id_categoria = categoria_producto.id_categoria WHERE nombre_producto= %(id)s',{'id':nombre_producto})
            data = cursor.fetchall()
            return data
        except Exception as e:
            return render_template('respuesta.html',respuesta = str(e))
        finally:
            cursor.close()
            con.close()

def agregarProducto(nombre_producto,stock,precio,categoria,tipo,detalle,file):
    try:
        con = mysql.connect()
        cursor = con.cursor()
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if len(buscarProducto(nombre_producto)) is 0:
                cursor.execute('INSERT INTO `producto`(`nombre_producto`, `stock_producto`, `precio_producto`, `id_categoria`, `id_tipo_producto`, `detalle_producto`, `direccion_foto_producto`, `activo`) VALUES (%(name)s,%(stock)s,%(price)s,%(cat)s,%(tipo)s,%(det)s,%(direc)s,1)',{'name':nombre_producto,'stock':stock,'price':precio,'cat':categoria,'tipo':tipo,'det':detalle,'direc':filename})
                data = cursor.fetchall()
                if len(data) is 0:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    con.commit()
                    return data
                else:
                    return data
            else:
                return data
        else:
            return data
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()


def getTipoProducto():
        try:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM `tipo_producto`')
            data = cursor.fetchall()
            return data
        except Exception as e:
            return render_template('respuesta.html',respuesta = str(e))
        finally:
            cursor.close()
            con.close()

def getCategoria():
        try:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM `categoria_producto`')
            data = cursor.fetchall()
            return data
        except Exception as e:
            return render_template('respuesta.html',respuesta = str(e))
        finally:
            cursor.close()
            con.close()
 

#ejecucion de la aplicacion
if __name__ == "__main__":
    app.run(debug=True)

