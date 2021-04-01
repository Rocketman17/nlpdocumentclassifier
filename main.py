from flask import Flask, render_template, flash
from flask import redirect, request, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import timedelta
import mysql.connector
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os, glob
import pickle
import sklearn

app=Flask(__name__)
model = pickle.load(open('Model.pickle', 'rb'))
app.secret_key=os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes= 2)

conn = mysql.connector.connect(host="sql5.freesqldatabase.com", user='sql5402571', password='kpw3krNuBR', database='sql5402571', auth_plugin='mysql_native_password')

cursor=conn.cursor(buffered=True)

@app.route('/')
def login():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('login.html')


@app.route('/register')
def register():
    if 'user_id' in session:
        session.permanent = True      
        return render_template('home.html')
    else:
        return render_template('register.html')


@app.route('/home')
def home():
    if 'user_id' in session:
        session.permanent = True      
        return render_template('home.html')
    else:
        return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    username=request.form.get('username')
    password=request.form.get('password')
    
    cursor.execute("""SELECT * FROM `newusers` WHERE `username` LIKE '{}' AND `password` LIKE '{}'""".format(username, password))
    users = cursor.fetchall()
    if len(users)>0:
        session['user_id']=users[0][0]
        return redirect('/home')
    else:
        flash('Incorrect credentials, Try again.', category='error')
        return redirect('/')

    return users

@app.route('/add_user', methods=['POST'])
def add_user():
    first_name = request.form.get('first_name')
    middle_name = request.form.get('middle_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    occupation = request.form.get('occupation')
    mail_address = request.form.get('mail_address')
    password = request.form.get('password')

    cursor.execute("""INSERT INTO `newusers` 
    (`first_name`, `middle_name`, `last_name`, `username`,
    `email`, `phone_number`, `occupation`, `mail_address`,
    `password`) VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(first_name, middle_name, last_name, username, email, phone_number, occupation, mail_address, password))
    conn.commit()

    cursor.execute("""SELECT * FROM `newusers` WHERE `username` LIKE '{}'""".format(username))
    myuser = cursor.fetchall()
    session['user_id']=myuser[0][0]
    return redirect('/home')


@app.route('/logout')
def logout():
     
    session.pop('user_id')
    return redirect('/')



@app.route('/query')
def query():

    print(request.query_string)

    return "No query received", 200

app.config["DOC_UPLOADS"] = "templates/static"
app.config['ALLOWED_DOC_EXTENSIONS'] = ["TXT", " "]

def allowed_doc(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_DOC_EXTENSIONS"]:
        return True
    else:
        return False

@app.route('/file_upload', methods=["GET", "POST"])
def file_upload():

    if request.method == "POST":

        if request.files:

            uploaded_file = request.files["document"]

            if uploaded_file.filename == "":
                flash("Document must have a filename", category="error")
                print("Document must have a filename")
                return redirect(request.url)

            # if not allowed_doc(uploaded_file.filename):
            #     print("This file extension is not allowed")
            #     return redirect(request.url)

            else:
                filename = secure_filename(uploaded_file.filename)

                uploaded_file.save(os.path.join(app.config["DOC_UPLOADS"], "temp.txt"))
                flash("file uploaded successfully", category="success")

            #print(uploaded_file)

            return redirect(request.url)

    return redirect ('/home')


@app.route('/predict_file', methods=['POST'])
def predict_file():


    path =  "templates/static/Data/"
    categories = ['alt.atheism','comp.graphics', 'comp.os.ms-windows.misc', 'comp.sys.ibm.pc.hardware',
 'comp.sys.mac.hardware', 'comp.windows.x', 'misc.forsale', 'rec.autos',
 'rec.motorcycles', 'rec.sport.baseball', 'rec.sport.hockey', 'sci.crypt',
 'sci.electronics', 'sci.med', 'sci.space', 'soc.religion.christian',
  'talk.politics.guns', 'talk.politics.mideast', 'talk.politics.misc', 'talk.religion.misc']

    for path, dir, files in os.walk(path):
        is_empty = os.listdir(path)
        if len(is_empty)==0:
            return redirect('/home')
        else:
            for f in files:
                file_name = os.path.join(path, f)
                with open(file_name, 'r') as dt:
                    d = dt.read()
                    #print(d)
                    pred = model.predict([d])
                    prediction = categories[pred[0]]        
    
    print("Files Deleting from delete_files")
    files = glob.glob("templates/static/temp.txt")
    for f in files:
        os.remove(f)
        
        return render_template('home.html', prediction = "Document belongs to {} category".format(prediction) )
    return redirect('/home')
    print("files Deleted from delete_files")
    
    return redirect('/home')




if __name__=="__main__":
    app.run(host='0.0.0.0' debug=True)
