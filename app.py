from flask import Flask,render_template, request, redirect, flash,url_for,abort
import pyodbc
import datetime
import webbrowser
from flask_sslify import SSLify


app = Flask(__name__,static_url_path='/static')

sslify = SSLify(app)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

global db2
db2=[]

def connection_U_P():
    server='x.x.x.x'
    bd='database'
    usuario='user'
    contrasena='password'
    try:
        conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL server}; SERVER='+server+';DATABASE='
                                      +bd+';UID='+usuario+';PWD='+contrasena)
        print('conexion exitosa')
    except Exception as e:
        print(e)
    return(conexion)

def connection_REPORTE():
    server='x.x.x.x'
    bd='database'
    usuario='user'
    contrasena='password'
    try:
        conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL server}; SERVER='+server+';DATABASE='
                                      +bd+';UID='+usuario+';PWD='+contrasena)
        print('conexion exitosa')
    except Exception as e:
        print(e)
    return(conexion)

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


@app.route('/nada')
def nada():
    if not redirect:
        return 'Redirect disabled'
    else:
        return redirect(url_for('ingreso'))

@app.route('/ingreso')
def home():
    #return 'Ingreso'
    return render_template('tabla.html',db=db2)

@app.route('/about')
def about():
    db=[]
    #return render_template('tabla.html',db=db)
    return 'About Page'

@app.route('/ejemplo')
def ejemplo():
    #return render_template ('ejemplo.html')
    return 'Ejemplo'

@app.route("/", methods = ['GET','POST'])
def ingreso():
    if request.method == 'GET':
        return render_template("ingreso.html")
    if request.method == 'POST':
        try:
            usuario = request.form["user"]
            contra = request.form["password"]
            db=[]
            conn=connection_U_P()
            cursor=conn.cursor()
            user="'"+usuario+"'"
            query="SELECT * FROM USUARIOS WHERE C_USUARIO = {}".format(user)
            cursor.execute(query)

            for row in cursor.fetchall():
                db.append({"usuario":row[0],"contra":row[3],"nombre":row[1]})
                nombre_usuario = row[1]
            conn.close()

            ##TABLA TOTAL
            db2=[]
            conn = connection_U_P()
            cursor=conn.cursor()
            cursor.execute('''
                        SELECT C_USUARIO,FE_ULT_CONEX,RU.REPORTES, RL.TITULO, RL.LINK, RL.DESCRIPCION
                        FROM  PORTALBI.REPORTES_BI_USUARIO RU LEFT JOIN PORTALBI.REPORTES_LINK RL ON RU.REPORTES = RL.REPORTES
                        WHERE C_USUARIO = {}
                        ORDER BY RL.TITULO ASC
                            ''')
            for row in cursor.fetchall():
                db2.append({"USUARIO":row[0].strip(),"DESCRIPCION":row[5],"C_REPORTE":row[2],"FECHA":row[1],"REPORTE":row[3],"LINK":row[4],"NOMBRE":nombre_usuario,"LLAVE":(row[0]+","+row[2]).replace(" ","")})  
            conn.close()
            print("USUARIO:",usuario)
            try:
                c=db[0]
                c=c["contra"]
                if contra==c:
                    print("si son iguales")
                    return render_template('tabla.html',db=db2,result=nombre_usuario,fecha_actual=datetime.datetime.now())
                    #return redirect(url_for("home"))
                else:
                    flash('CONTRASEÑA INCORRECTA')
                    return redirect ('/')
            except Exception as e:
                print(e)
                flash('ERROR USUARIO')
                return redirect ('/')
        except:
            pass

        try:
            llave = request.form["ID"]
            c_usuario,reporte=llave.split(",")
            reporte="'"+reporte+"'" 
            c_usuario ="'"+c_usuario+"'" 
            tiempo = datetime.datetime.now()
            tiempo = tiempo.strftime("%Y-%m-%d %H:%M:%S")
            tiempo = "'"+tiempo+"'" 
            conn = connection_U_P()
            cursor=conn.cursor()
            cursor.execute('''
                        SELECT LINK FROM PORTALBI.REPORTES_LINK WHERE REPORTES = {}
                            '''.format(reporte))
            link = cursor.fetchall()
            link = link[0][0]
            conn.close()

            print("Insertar tiempo...")
            conn = connection_U_P()
            cursor=conn.cursor()
            query='UPDATE PORTALBI.REPORTES_BI_USUARIO SET FE_ULT_CONEX = CONVERT(DATETIME,{},20) WHERE C_USUARIO = {} AND REPORTES = {}'.format(tiempo,c_usuario,reporte)
            cursor.execute(query)
            conn.commit()
            print('QUERY')
            print(query)
            print("Tiempo insertado!")
            return redirect (link) #----------->
 
        except Exception as e:
            print(e)
            return redirect ("Error")
 
if __name__=='__main__':
    from waitress import serve
    app.run(port=8001)
