import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session ,url_for,send_file
from base64 import b64encode, b64decode
from vault import application
from vault import blob_service_client
from vault import bcrypt
from vault import db
from vault.helpers import apology, login_required
from vault.models import User, FileTable
import face_recognition
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from PIL import Image
from io import BytesIO
import zlib

import tempfile
@application.route("/")
@login_required
def home():

    return redirect("/home")

@application.route("/home")
@login_required
def index():
    files = FileTable.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html",files=files)


@application.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""


 
    if request.method == "POST":

        # Assign inputs to variables
        input_username = request.form.get("username")
        input_password = request.form.get("password")

 
        if not input_username:
            return render_template("login.html",messager = 1)


        elif not input_password:
             return render_template("login.html",messager = 2)


        user = User.query.filter_by(username=input_username).first() 

        # if user is None or not check_password_hash(user.password, input_password):
       # if user is None:
        if user is None or not bcrypt.check_password_hash(user.password, input_password):
            return render_template("login.html",messager = 3)

        # Remember which user has logged in
        session["user_id"] = user.id
        session['user_name'] = user.username

        return redirect("/")

    else:
        return render_template("login.html")


@application.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@application.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        input_username = request.form.get("username")
        input_email = request.form.get("email")
        input_password = request.form.get("password")
        input_confirmation = request.form.get("confirmation")

        if not input_username:
            return render_template("register.html",messager = 1)

        elif not input_password:
            return render_template("register.html",messager = 2)

        elif not input_confirmation:
            return render_template("register.html",messager = 4)

        elif not input_password == input_confirmation:
            return render_template("register.html",messager = 3)

        user = User.query.filter_by(username=input_username).first()   


        if (user):
            return render_template("register.html",messager = 5)

        else:
            hashed_password=bcrypt.generate_password_hash(input_password)
            new_user = User(username=input_username,email=input_email,password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            if new_user:
                session["user_id"] = new_user.id

            flash(f"Registered as {input_username}")

            # Redirect user to homepage
            return redirect("/")


    else:
        return render_template("register.html")




@application.route("/facereg", methods=["GET", "POST"])
def facereg():
    session.clear()
    if request.method == "POST":


        encoded_image = (request.form.get("pic")+"==").encode('utf-8')
        input_username = request.form.get("name")
        user = User.query.filter_by(username=input_username).first()
              
        if user is None:
            return render_template("camera.html",message = 1)

        id_ = user.id    
        compressed_data = zlib.compress(encoded_image, 9) 
        
        uncompressed_data = zlib.decompress(compressed_data)
        
        decoded_data = b64decode(uncompressed_data)
        new_image_handle = open('vault/static/face/unknown/'+str(id_)+'.jpg', 'w+b')
        
        new_image_handle.write(decoded_data)
        new_image_handle.close()
        container_client = blob_service_client.get_container_client(container=os.getenv('AZURE_CONTAINER_NAME')) 
        with tempfile.TemporaryFile(mode='w+b') as f:
            # s3.download_fileobj(os.getenv("BUCKET_NAME"), str(id_)+'.jpg', f)
            f.write(container_client.download_blob(str(id_)+'.jpg').readall())
                    
            try:
                # image_of_bill = face_recognition.load_image_file(
                # './static/face/'+str(id_)+'.jpg')
                image_of_bill = face_recognition.load_image_file(f)
            except:
                return render_template("camera.html",message = 5)

            bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]

            unknown_image = face_recognition.load_image_file(
            'vault/static/face/unknown/'+str(id_)+'.jpg')
            try:
                unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
            except:
                return render_template("camera.html",message = 2)
            f.close()


#       compare faces
        results = face_recognition.compare_faces([bill_face_encoding], unknown_face_encoding,tolerance=0.5)

        if results[0]==True:
            user = User.query.filter_by(username=input_username).first()
            session["user_id"] = user.id
            session['user_name'] = user.username
            os.remove('vault/static/face/unknown/'+str(id_)+'.jpg')
            return redirect("/")
        else:
            os.remove('vault/static/face/unknown/'+str(id_)+'.jpg')
            return render_template("camera.html",message=3)


    else:
        return render_template("camera.html")



@application.route("/facesetup", methods=["GET", "POST"])
def facesetup():
    if request.method == "POST":
        encoded_image = (request.form.get("pic")+"==").encode('utf-8')
        id_=User.query.filter_by(id=session["user_id"]).first().id
        # id_ = db.execute("SELECT id FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["id"]    
        compressed_data = zlib.compress(encoded_image, 9) 
        
        uncompressed_data = zlib.decompress(compressed_data)
        decoded_data = b64decode(uncompressed_data)
        
        new_image_handle = open('vault/static/face/'+str(id_)+'.jpg', 'wb')
        
        new_image_handle.write(decoded_data)
        new_image_handle.close()
        image_of_bill = face_recognition.load_image_file(
        'vault/static/face/'+str(id_)+'.jpg')    
        print(str(id_)+'.jpg')
        try:
            bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]
        except:    
            return render_template("face.html",message = 1)
        blob_client = blob_service_client.get_blob_client(container=os.getenv('AZURE_CONTAINER_NAME'), blob=str(id_)+'.jpg')
        with open(file='vault/static/face/'+str(id_)+'.jpg', mode="rb") as data:
            blob_client.upload_blob(data)
        # s3.upload_file('vault/static/face/'+str(id_)+'.jpg',os.getenv("BUCKET_NAME"),str(id_)+'.jpg')
        os.remove('vault/static/face/'+str(id_)+'.jpg')
        return redirect("/home")

    else:
        return render_template("face.html")
    
@application.route("/upload",methods=["GET","POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['inputFile']
        data = file.read()   
        newFile = FileTable(name=file.filename, file=data,user_id=session["user_id"])
        db.session.add(newFile)
        db.session.commit()
        return render_template("upload.html",message=1)
    else:
        return render_template("upload.html")
    
@application.route('/retrieve/<id>')
def retrieve(id):
    file = FileTable.query.filter_by(id=id).first()

    if not file:
        return render_template('error.html')

    return send_file(BytesIO(file.file), download_name=f'{file.name}')

@application.route('/delete/<id>')
def delete(id):
    file = FileTable.query.filter_by(id=id).first()

    if not file:
        return render_template('error.html')

    db.session.delete(file)
    db.session.commit()

    return redirect(url_for('index'))
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html",e = e)


# Listen for errors
for code in default_exceptions:
    application.errorhandler(code)(errorhandler)