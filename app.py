from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import MySQLdb
import os

import math



with open ('config.json','r') as c:
    params = json.load(c)['params']


local_server=params['local_server']



app = Flask(__name__)


app.secret_key = params['secret_key'] 

#app.config['SESSION_COOKIE_SECURE'] = True
#app.config['REMEMBER_COOKIE_SECURE'] = True


if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_num = db.Column(db.String(10), unique=True, nullable=False)
    message= db.Column(db.String(100), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=False)


class posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    tagline = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(25), unique=True, nullable=False)
    content = db.Column(db.String(180), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=False)
    whom = db.Column(db.String(30), unique=False, nullable=False)
    image_url = db.Column(db.String(200), unique=False, nullable=False)

x = int(params['no_of_post'])
                                                                                                                                                                                                                                                                                                                                                                                                                                       
@app.route("/")
def home():

    all_post = posts.query.filter_by().all()
    last = math.ceil(len(all_post)/x)

    page = request.args.get('page')
    
    if(not str(page).isnumeric()):
        page = 1
    page=int(page)

    all_post = all_post[(page-1)*x:page*x]

    if(page==1):
        prev = '#'
        next = '/?page=' + str(page+1)

    elif(page==last):
        next = '#'
        prev = '/?page=' + str(page-1)

    else:
        next = '/?page=' + str(page+1)
        prev = '/?page=' + str(page-1)


    return render_template('index.html',params=params,posts=all_post,prev=prev, next=next)
    


@app.route("/about")
def about():
    return render_template('about.html',params=params)

    
@app.route("/post/<string:post_slug>" , methods = ['GET'])
def post_page(post_slug):
    post=posts.query.filter_by(slug = post_slug).first()

    return render_template('post.html',params=params, post=post)



@app.route("/dashboard",methods=['POST','GET'])
def dashboard():
    all_posts = posts.query.all()
    if('user' in session and session['user']==params['admin_user']):
        return render_template('dashboard.html',params=params,post=all_posts)


    if(request.method=='POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        

        if(username==params['admin_user'] and password==params['admin_pass']):
            session['user'] = username
            return render_template('dashboard.html',params=params, post=all_posts)
        return "wrong inputs...!!!"

    return render_template("signup.html",params=params)



@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user']==params['admin_user']):
        post = posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')
    return "u cannot do that pls get lost"



@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            get_tagline = request.form.get('tagline')
            get_title = request.form.get('title')
            get_slug = request.form.get('slug')
            get_image_url = request.form.get('image_url')
            get_content = request.form.get('content') 
            get_date = datetime.now()

            if sno=='0':
                new_entry = posts(title=get_title, tagline=get_tagline, slug=get_slug, image_url=get_image_url, content=get_content, date=get_date,whom="Admin")
                db.session.add(new_entry)
                db.session.commit()

            else:
                post = posts.query.filter_by(sno=sno).first()
                post.title = get_title
                post.tagline = get_tagline
                post.slug = get_slug
                post.image_url = get_image_url
                post.content = get_content
                post.date = get_date
                db.session.commit()
                return redirect('/dashboard')
            
        post1 =posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post1,sno=sno)
    return "u cannot enter"




@app.route("/upload_file", methods=['POST','GET'])
def upload():
    if('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            f = request.files.get('ufile')
            f.save(os.path.join(params['file_location'] , secure_filename(f.filename) ))
            return "upload success"

        return render_template('upload.html')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')



@app.route("/contact" , methods = ['GET','POST'] )
def contact():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone_num=request.form.get('phone_num')
        message=request.form.get('message')
        date=datetime.now()

        entry = contacts(name=name, phone_num=phone_num, message=message, email=email, date=date)

        db.session.add(entry)
        db.session.commit()


    return render_template('contact.html',params=params)


app.run(debug=True)

