import email
from functools import partial
from os import abort, name, path
from typing import final
from xml.etree.ElementTree import PI
from flask import Flask
from flask import render_template,redirect,url_for,request,abort
from flask import json
from flask.helpers import flash
from flask.json import jsonify
from flask.wrappers import Response
from flask_sqlalchemy.model import Model
from flask_wtf import FlaskForm
from flask_wtf import file
from flask_wtf.file import FileField, FileAllowed
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import session
from werkzeug.datastructures import Range
from werkzeug.local import F
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields import choices
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
#from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os, os.path
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import random
from http import HTTPStatus
from io import BufferedReader
from datetime import date, datetime
from wtforms.validators import NumberRange
from wtforms.widgets.core import NumberInput
from flask import make_response
import boto3
from config import S3_BUCKET, S3_KEY, S3_SECRET
import base64
import requests
from bs4 import BeautifulSoup



events = [
    {
        'name' : '',
        'lastname' : '',
        'date': '',
        'time':'',
        'tel': '',
        'note': '',
        'url': '',
        'email': ''
    }
]

s3 = boto3.client(
    's3',
    aws_access_key_id = S3_KEY,
    aws_secret_access_key = S3_SECRET)

application = Flask(__name__)
application.config['SECRET_KEY'] ='Thisissupposedtobesecret!'


#OLD SQLITE DB
#application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#NEW MYSQL DB
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1745easd@storetohome.cvzew6buotnj.eu-central-1.rds.amazonaws.com/storetohome'
bootstrap = Bootstrap(application)

db = SQLAlchemy(application)

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'
UPLOAD_FOLDER = './static/pics'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config.from_pyfile('config.cfg')

admin = Admin(application)

mail = Mail(application)

s = URLSafeTimedSerializer('Thisisasecret!')



@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), unique=True)
    lastname = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(250))
    phonenumber = db.Column(db.BigInteger())
    partnership = db.Column(db.String(30))
    region = db.Column(db.String(30))
    afm = db.Column(db.Integer())
    is_admin = db.Column(db.Boolean, default = False)
    token = db.Column(db.String(300), unique=True)
    email_verification_token= db.Column(db.String(300), unique=True)
    email_verified = db.Column(db.Boolean, default = False)
    datetime_account_creation = db.Column(db.String(30))

class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(150))

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16))
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    title = db.Column(db.String(150))
    description = db.Column(db.String(500))
    region = db.Column(db.String(50))
    address = db.Column(db.String(50))
    category = db.Column(db.String(200))
    tmprice = db.Column(db.String(15))
    emvado = db.Column(db.Integer())
    rooms = db.Column(db.Integer())
    floor = db.Column(db.String(100))
    year = db.Column(db.Integer())
    heat = db.Column(db.String(150))
    price = db.Column(db.Integer())
    partnership = db.Column(db.String(30))
    photo = db.Column(db.String(500))
    pic = db.Column(db.String(200))

    

class UserInterest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50))   
    lastname = db.Column(db.String(50))
    email_endiaferomenou = db.Column(db.String(40))
    email_idiokthth = db.Column(db.String(40))
    number = db.Column(db.String(30))
    code = db.Column(db.String(100))
    status = db.Column(db.String(30))
    deal = db.Column(db.String(30))
    datetime = db.Column(db.String(30))

class Partners_Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerfirstname = db.Column(db.String(50))   
    customerlastname = db.Column(db.String(50))
    partner_firstname = db.Column(db.String(50))
    partner_lastname = db.Column(db.String(50))
    email_to = db.Column(db.String(40))
    customer_phonenumber = db.Column(db.String(40))
    partnerphonenumber = db.Column(db.String(40))
    code = db.Column(db.String(20))
    

class Second_Tier_Partner_Deals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_code = db.Column(db.String(20))
    firstname = db.Column(db.String(50))   
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(40))
    partner_number = db.Column(db.String(40))
    partnership = db.Column(db.String(40))
    deal_at = db.Column(db.String(40))
    datetime_deal = db.Column(db.String(50))
    job = db.Column(db.String(20))

class Last_deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_code = db.Column(db.String(20))
    firstname = db.Column(db.String(50))   
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(40))
    partner_number = db.Column(db.String(40))
    partnership = db.Column(db.String(40))
    deal_at = db.Column(db.String(40))
    datetime_deal = db.Column(db.String(50))

class Ad_Backlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16))
    seller_firstname = db.Column(db.String(50))
    seller_lastname = db.Column(db.String(50))
    seller_username = db.Column(db.String(50))
    seller_number = db.Column(db.String(50))
    email = db.Column(db.String(50))
    title = db.Column(db.String(250))
    description = db.Column(db.String(300))
    region = db.Column(db.String(50))
    address = db.Column(db.String(50))
    category = db.Column(db.String(200))
    tmprice = db.Column(db.String(15))
    emvado = db.Column(db.Integer())
    rooms = db.Column(db.Integer())
    floor = db.Column(db.String(100))
    year = db.Column(db.Integer())
    heat = db.Column(db.String(150))
    price = db.Column(db.Integer())
    
class Deal_Backlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16))
    buyer_firstname = db.Column(db.String(30))
    buyer_lastname = db.Column(db.String(30))
    buyer_number = db.Column(db.String(50))
    deal_mesiti = db.Column(db.String(30))
    firstname_diakosmiti =db.Column(db.String(50))
    lastname_diakosmiti =db.Column(db.String(50))
    phonenumber_diakosmiti = db.Column(db.String(50))
    firstname_mhxanikou =db.Column(db.String(50))
    lastname_mhxanikou =db.Column(db.String(50))
    phonenumber_mhxanikou = db.Column(db.String(50))
    firstname_ergolavou =db.Column(db.String(50))
    lastname_ergolavou =db.Column(db.String(50))
    phonenumber_ergolavou = db.Column(db.String(50))
    deal_diakosmiti = db.Column(db.String(30))
    deal_mhxanikou = db.Column(db.String(30))
    deal_ergolavou = db.Column(db.String(30))
    partner_sum = db.Column(db.Float())
    sell_cost = db.Column(db.Float())
    bprofit = db.Column(db.Float())
    datetime = db.Column(db.String(30))

class Pictures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adcode = db.Column(db.String(16))
    filename = db.Column(db.String(200))

class Rantevou(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    arithmos_rantevou = db.Column(db.String(16))
    onoma_kataxwrith = db.Column(db.String(50))
    eponimo_kataxwrith = db.Column(db.String(50))
    hmeromhnia_rantevou = db.Column(db.String(50))
    wra_rantevou = db.Column(db.String(50))
    onoma_endiaferomenou = db.Column(db.String(50))
    eponimo_endiaferomenou = db.Column(db.String(50))
    thlefwno = db.Column(db.String(200))
    simeiwseis = db.Column(db.String(500))
    email = db.Column(db.String(50))


class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_admin == True:
            return current_user.is_authenticated
        else:
            return abort(403)
    
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Ad, db.session))
admin.add_view(MyModelView(UserInterest, db.session))
admin.add_view(MyModelView(Partners_Assignment, db.session))
admin.add_view(MyModelView(Second_Tier_Partner_Deals, db.session))
admin.add_view(MyModelView(Last_deal, db.session))
admin.add_view(MyModelView(Ad_Backlog, db.session))
admin.add_view(MyModelView(Deal_Backlog, db.session))
admin.add_view(MyModelView(Links, db.session))
admin.add_view(MyModelView(Pictures, db.session))
admin.add_view(MyModelView(Rantevou, db.session))




    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
 

class LoginForm(FlaskForm):
    username = StringField('Όνομα Χρήστη', validators=[InputRequired(), Length(min=4,max=15)])
    password = PasswordField('Κωδικός', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    firstname = StringField('Όνομα', validators=[InputRequired(), Length(min=4,max=30)])
    lastname = StringField('Επώνυμο', validators=[InputRequired(), Length(min=4,max=30)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('Όνομα Χρήστη', validators=[InputRequired(), Length(min=4,max=15)])
    password = PasswordField('Κωδικός', validators=[InputRequired(), Length(min=8, max=80)])
    phonenumber = IntegerField('Τηλέφωνο', validators=[NumberRange(min=0, max=800000000000)])
    partnership = SelectField('Συνεργασια', choices=[('Απλός Χρήστης'),('Μεσίτης'),('Μηχανικός'),('Διακοσμητής'),('Συμβολαιογράφος'),('Εργολάβος'),('Δικηγόρος')])
    region = SelectField('Περιοχή', choices=[('Αθήνα'),('Θεσσαλονίκη'),('Πάτρα'),('Λάρισα'),
    ('Βόλος'),('Ιωάννινα'),('Ηράκλειο'),('Αλεξανδρούπολη')])

class ForgotYourPassword(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])

class ChangePassword(FlaskForm):
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@application.route('/', methods = ['GET', 'POST'])
def arxikh():
    image_names=os.listdir('./static/pics')
    print(image_names)
    adv = Ad.query.all()
    array = []
    
    if request.method == 'POST':
        region = request.form.get('region')
        qty = int(request.form.get('qty'))
        max = int(request.form.get('max'))
        min = int(request.form.get('min'))
        

        if adv:
            return render_template('filtered.html', adv = adv, region = region, qty = qty, max = max, min = min)
        else:
            return render_template('filtered.html')
    if adv:
        for ad in adv:
            array.append(ad)
    print(events)
    return render_template('main.html', image_names = image_names, current_user = current_user,array = array, adv = adv)


@application.route('/filtered')
def filtered():
    return render_template('filtered.html')


@application.route('/links', methods = ['GET','POST'])
def links():
    if current_user.is_admin:
        if request.method == 'POST':
            link = request.form.get('link')
            new_link = Links(link = link)
            db.session.add(new_link)
            db.session.commit()
            flash('Καταχωρήθηκε το link {}'.format(link))
    return render_template('account/links.html')
    

@application.route('/myAccount', methods=['GET', 'POST'])
@login_required
def myAccount():
    user = User.query.filter_by(username = current_user.username).first()
    if request.method == 'POST':
        afm = request.form.get('afmnum')
        user.afm = afm
        db.session.commit()
    return render_template('/account/myAccount.html', current_user = current_user)




@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    userexists = User.query.filter_by(username=form.username.data).first()
    #if userexists:
    if current_user.is_authenticated:
        return redirect(url_for('myAccount'))
    elif form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data) or user.password == form.password.data:
                if login_user(user, remember=form.remember.data):
                    return(redirect(url_for('myAccount')))
            else: 
                flash('Λάθος όνομα χρήστη ή κωδικός.')
                return(redirect(url_for('login'))) 
        else: 
            flash('Ο χρήστης δεν υπάρχει.')
            return(redirect(url_for('login')))  
    return render_template('login.html', form = form, userexists = userexists)
    

@application.route('/signup', methods=['GET', 'POST'])
def signup():
    form= RegisterForm()

    if form.validate_on_submit():
        username=User.query.filter_by(username=form.username.data).first()
        useremail=User.query.filter_by(email=form.email.data).first()

        if username or useremail:
            flash('Usename or password already exists')
            return redirect(url_for('signup'))
        else:
            email = request.form['email']
            token = s.dumps(email, salt = 'email-confirm')

            msg = Message('Confirm Email', sender = 'heroku@seaplaellinika.gr', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)

            msg2 = Message('Ενας νέος χρήστης εγγράφηκε στο StoreToHome', sender = 'heroku@seaplaellinika.gr', recipients= ['dhspapa@yahoo.gr'])
            msg2.body = 'Ο χρήστης με email: {} έκανε εγγραφή στο StoreToHome'.format(email)
            mail.send(msg2)

            hashed_password = generate_password_hash(form.password.data, method = 'sha256')
            new_user=User(firstname = form.firstname.data, lastname = form.lastname.data,username=form.username.data, email= form.email.data, password=hashed_password, phonenumber=form.phonenumber.data ,partnership=form.partnership.data, region = form.region.data, email_verification_token = token,datetime_account_creation=datetime.now())
            #new_user=User(username=form.username.data, email= form.email.data, password=form.password.data,partnership=form.partnership.data)
            db.session.add(new_user)
            db.session.commit()
        return render_template('checkmail.html')

    return render_template('signup.html', form=form)


@application.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        verifyemail = User.query.filter_by(email_verification_token = token).first()
        email = s.loads(token, salt='email-confirm', max_age=360)
    except SignatureExpired:
        return 'The token expired'
    verifyemail.email_verified = True
    db.session.commit()
    return 'Account Verified'



@application.route('/cal')
def cal():
    if current_user.is_authenticated:
        return render_template('cal.html', events=events, current_user = current_user )
    else:
        return('Δεν είσαι εγγεγραμένος στο StoreToHome..')


@application.route('/rantevou', methods = ["GET", "POST"])
def rantevou():
    if current_user.is_authenticated:
        if current_user.partnership != ' ' or current_user.partnership != None:
            if request.method == 'POST':
                date = request.form.get('date')
                time = request.form.get('time')
                name = request.form.get('name')
                srname = request.form.get('srname')
                tel = request.form.get('tel')
                note = request.form.get('note')
                code = str(random.getrandbits(16))
                print(date)
                print(time)
                print(name)
                print(srname)
                print(tel)
                print(note)
                
                synolo = Rantevou(arithmos_rantevou = code, onoma_kataxwrith = current_user.firstname,  eponimo_kataxwrith = current_user.lastname, email = current_user.email, onoma_endiaferomenou = name, eponimo_endiaferomenou = srname, hmeromhnia_rantevou = date, wra_rantevou = time, thlefwno = tel, simeiwseis = note ) 
                db.session.add(synolo)
                db.session.commit()  
                #events.append({
                 #   'name': name,
                  #  'lastname': srname,
                   # 'date' : date,
                    #'time' : time,
                    #'tel' : tel,
                    #'note' : note,
                    #'url': 'http://127.0.0.1:5000/rant/{}'.format(code),
                    #'email': '{}'.format(current_user.email)

                #},)
                events.append({
                    'name': synolo.onoma_endiaferomenou,
                    'lastname':synolo.eponimo_endiaferomenou,
                    'date' : synolo.hmeromhnia_rantevou,
                    'time' : synolo.wra_rantevou,
                    'tel' : synolo.thlefwno,
                    'note' : synolo.simeiwseis,
                    'url': 'https://storetohome.gr/rant/{}'.format(synolo.arithmos_rantevou),
                    'email': '{}'.format(current_user.email)

                },)     
                return redirect(url_for('cal'))

            return render_template('rantevou.html')
    else:
        return('Δεν είσαι συνεργάτης στο StoreToHome..')
        

@application.route('/rant/<code>')
def rant(code):
    if current_user.is_authenticated:
        rantevou = Rantevou.query.filter_by(arithmos_rantevou = code).first()
        print(rantevou)
        return render_template('rant.html',rantevou = rantevou)
    else:
        return('Δεν είσαι εγγεγραμένος στο StoreToHome..')


@application.route('/add' , methods = ["GET", "POST"])
@login_required
def add():
    
    if request.method == 'POST':
        firstname = current_user.firstname
        lastname = current_user.lastname
        user=current_user.username
        email = current_user.email
        partnership = current_user.partnership
            
        
        files = request.files.getlist('files[]') 
        title = request.form.get('title')
        description = request.form.get('description')
        region = request.form.get('region')
        address = request.form.get('address')
        category = request.form.get('category')        
        tmprice = request.form.get('tmprice')        
        emvado = request.form.get('emvado')        
        rooms = request.form.get('rooms')        
        floor = request.form.get('floor')        
        year = request.form.get('year') 
        heat = request.form.get('heat')        
        price = request.form.get('price')        
        code = str(random.getrandbits(16))
        
        
        datafiles = []

      
        for file in files:
            f = file.filename
            datafiles.append(f)
            jsonlist = json.dumps(datafiles)
            filename = secure_filename(file.filename)
            pictures = Pictures(adcode = code, filename = filename)
            db.session.add(pictures)
            file.save(filename)
            s3.upload_file(
                Bucket = S3_BUCKET,
                Filename = filename,
                Key = filename, 
                 ExtraArgs={ "ContentType": "image/jpeg"}
            )
        

        
        ad = Ad(firstname = firstname, lastname = lastname,username = user , email = email, code = code, title=title, description = description, address = address, region = region, category = category,tmprice = tmprice, emvado = emvado, rooms = rooms, floor = floor, year = year, heat = heat, price = price, partnership = partnership,photo = jsonlist, pic = filename)   
        adbacklog = Ad_Backlog(code = code, seller_firstname = firstname, seller_lastname = lastname, seller_username = user,seller_number = current_user.phonenumber, email = email, title = title, description = description, address = address, region = region , category = category, tmprice = tmprice, emvado = emvado, rooms = rooms,
        floor = floor, year = year, heat = heat, price = price)
        db.session.add(adbacklog)
        db.session.add(ad)
        
        db.session.commit()  
#########################################################################################
           
#########################################################################################           
        return redirect(url_for('akinhta', code = code))
    return render_template('add.html', name=current_user.username)



@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')



@application.route('/aggelies/<int:page_num>')
def aggelies(page_num):
    

    registries = Ad.query.all()
    reg_list = []
    pics_view = []
    total = []
    codes = []
    totreg = []
    aggls = Ad.query.paginate(per_page = 10, page = page_num, error_out = True)
   

    file_names=os.listdir('./static/pics/')
    pics_view.append(file_names)

    for registry in registries:
        reg_list.append(registry.photo)
        codes.append(registry.code)
        totreg.append(registry)
        
    print(codes)


    for reg in reg_list:
        print(reg)
        for view in pics_view:
            for x in view:
                if x in reg:
                    total.append(x)
                    break

    return render_template("aggelies.html", totreg = totreg, current_user = current_user, aggls = aggls)



@application.route('/akinhta/<code>', methods = ["GET", "POST"])
def akinhta(code):
     

    routes = Ad.query.all()
    images = []
    pic_names = []
    check_deal = Deal_Backlog.query.filter_by(code = code).first()
    

    for route in routes:
        if code in route.code:
            adcode = route.code
            adusername = route.username
            ademail = route.email
            adtitle = route.title
            addescription = route.description
            adregion = route.region
            adaddress = route.address
            adcategory = route.category
            adtmprice = route.tmprice
            ademvado = route.emvado
            adrooms = route.rooms
            adfloor = route.floor 
            adyear = route.year
            adheat = route.heat
            adprice = route.price
            photo = route.photo
            
    pictures = Pictures.query.all()
    pic_folder = []

    for picture in pictures:
        if picture.adcode == code:
            pic_folder.append(picture.filename)
            print(pic_folder)

    get_front_pic = Ad.query.filter_by(code = code).first()
    front_pic = get_front_pic.pic


    
    
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['firstname']
        lname = request.form['lastname']
        number = request.form['telnum']
        #region = request.form['region']
        description = request.form['subject']

        print(email)
        user_interest = UserInterest(firstname = fname , lastname = lname, email_endiaferomenou = email, email_idiokthth = ademail, number = number, code = code, status = 'Pending')
        db.session.add(user_interest)
        db.session.commit()
        #userinterest = UserInterest.query.filter_by(code = code).first()

        #partners=User.query.filter_by(partnership='Μεσίτης').all()
        
        #for partner in partners:
        msg = Message('Δήλωση ενδιαφέροντος', sender = 'heroku@seaplaellinika.gr', recipients=[ademail])
        msg.body = 'Ο/Η {} {} με αριθμό επικοινωνίας {} και email {} , ενδιαφέρεται για την αγγελία με αριθμό {} και λέει: {}'.format(fname,lname,number,email,adcode,description)
        mail.send(msg)  
        return render_template('sendemail.html')


    
    return render_template('/akinhta.html', pic_names = pic_names, photo = photo, adcode = adcode, adusername = adusername, ademail = ademail, 
    adtitle = adtitle, addescription = addescription, adregion = adregion, adaddress = adaddress,
    adcategory = adcategory,adtmprice = adtmprice,ademvado = ademvado, adrooms = adrooms, adfloor = adfloor, adyear = adyear, adheat = adheat, adprice = adprice,
    code = code, check_deal = check_deal, pic_folder = pic_folder, front_pic = front_pic,pictures = pictures)



@application.route('/notifications', methods = ['GET','POST'])
@login_required
def notifications():
    if current_user.is_authenticated:
        notifications = UserInterest.query.all()
        ads = Ad.query.all()
        advs = []
        aggelies = []
        sent = []
        codes = []
        if ads:
            for notification in notifications:
                if notification.email_idiokthth == current_user.email:
                    for ad in ads:
                        if ad.code == notification.code:
                            aggelies.append(notification)
                codes.append(notification.code)
                print(codes)
                        
                            

                if notification.code in codes:
                    if notification.deal != None:
                
                        advert = Ad.query.filter_by(code = notification.code).first()
                        if advert:
                            if current_user.region == advert.region:
                                if current_user.partnership == 'Διακοσμητής' or current_user.partnership == 'Μηχανικός':
                                    sent.append(notification)
                                if current_user.partnership == 'Εργολάβος':
                            #locked = Second_Tier_Partner_Deals.query.all()
                                    locked_by_engineer = Second_Tier_Partner_Deals.query.filter_by(ad_code = notification.code, partnership = 'Μηχανικός').first()
                                    locked_by_decorator = Second_Tier_Partner_Deals.query.filter_by(ad_code = notification.code, partnership = 'Διακοσμητής').first()
                            
                                    if locked_by_engineer and locked_by_decorator:
                                        if locked_by_decorator.job == 'Completed' and  locked_by_engineer.job == 'Completed':
                                            advs.append(notification)
        
    return render_template("account/notifications.html", aggelies = aggelies, sent = sent, current_user = current_user, advs=advs, ads = ads)


@application.route('/interest/<id>', methods = ['GET','POST'])
def interest(id):
    ad = UserInterest.query.filter_by(id = id).first()
    adv = Ad.query.filter_by(id = id).first()
    if request.method == "POST":
        value = request.form.get("status")
        if value == '1':
            ad.status = 'Accepted'
        else:
            ad.status = 'Denied'
        ad.deal = ''
        db.session.commit()
        return redirect(url_for('notifications'))        
    return render_template("account/interest.html", ad=ad, adv = adv,current_user = current_user)


@application.route('/prosfora/<id>' , methods = ['GET','POST'])
@login_required
def prosfora(id):
    if current_user.is_authenticated:
        users = User.query.all()
        ad = UserInterest.query.filter_by(id = id).first()
        advert = Ad.query.filter_by(code = ad.code).first()
        if ad.deal == '':
            if request.method == "POST":
                deal = request.form.get("deal")
                ad.datetime = datetime.now()
                ad.deal = deal
                
                dealbacklog = Deal_Backlog(code = ad.code, buyer_firstname = ad.firstname, buyer_lastname = ad.lastname,
                buyer_number = ad.number, deal_mesiti = deal)
                db.session.add(dealbacklog)

                for user in users:
                    if user.partnership == 'Διακοσμητής' or user.partnership == 'Μηχανικός':
                        if user.region == advert.region:
                            msg = Message('Διαθέσιμες εργασίες', sender = 'heroku@seaplaellinika.gr', recipients=[user.email])
                            msg.body = 'Υπάρχουν διαθέσιμες εργασίες για το ακινητο της αγγελίας #{} που αγοράστηκε απο τον/την {} {}'.format(ad.code,ad.firstname,ad.lastname)
                            mail.send(msg)
                            assing_job=Partners_Assignment(customerfirstname=ad.firstname, customerlastname= ad.lastname, partner_firstname = user.firstname, partner_lastname = user.lastname, email_to = user.email, customer_phonenumber = ad.number, partnerphonenumber=user.phonenumber,code = ad.code)
                            db.session.add(assing_job)
                            db.session.commit()
                db.session.commit()
            
    return render_template('/account/prosfora.html', adcode = ad.code, adname = ad.firstname, adlname = ad.lastname, adnumber = ad.number, deal = ad.deal, current_user = current_user, advert = advert)



@application.route('/offer/<code>', methods = ['GET','POST'])
def offer(code):
    ad = Ad.query.filter_by(code = code).first()
    number = UserInterest.query.filter_by(code = code).first()
    if current_user.is_authenticated:
         if current_user.partnership == 'Διακοσμητής' or current_user.partnership == 'Μηχανικός':
            if request.method == "POST":
                if request.form["btn"]=="Submit":
                    deal = request.form.get("deal")
                    partner_deal = Second_Tier_Partner_Deals(ad_code=code,firstname = current_user.firstname, lastname = current_user.lastname,email=current_user.email,
                    partner_number=current_user.phonenumber,partnership=current_user.partnership,deal_at=deal,datetime_deal=datetime.now())
                    db.session.add(partner_deal)
                    dealbacklog = Deal_Backlog.query.filter_by(code = code).first()
                    if current_user.partnership == 'Διακοσμητής':    
                        dealbacklog.firstname_diakosmiti = current_user.firstname
                        dealbacklog.lastname_diakosmiti = current_user.lastname
                        dealbacklog.phonenumber_diakosmiti = current_user.phonenumber
                        dealbacklog.deal_diakosmiti = deal
                    elif current_user.partnership == 'Μηχανικός':    
                        dealbacklog.firstname_mhxanikou = current_user.firstname
                        dealbacklog.lastname_mhxanikou = current_user.lastname
                        dealbacklog.phonenumber_mhxanikou = current_user.phonenumber
                        dealbacklog.deal_mhxanikou = deal
                    db.session.commit()
                    return redirect(url_for('notifications'))

                if request.form["btn"]=="Complete":
                    done = 'Completed'
                    job = Second_Tier_Partner_Deals.query.filter_by(ad_code = code, partnership = current_user.partnership).first()
                    job.job = done
                    db.session.commit()

                    locked_by_engineer = Second_Tier_Partner_Deals.query.filter_by(ad_code = code, partnership = 'Μηχανικός').first()
                    locked_by_decorator = Second_Tier_Partner_Deals.query.filter_by(ad_code = code, partnership = 'Διακοσμητής').first()
                    if locked_by_decorator and locked_by_engineer:
                        if locked_by_decorator.job == 'Completed' and locked_by_engineer.job == 'Completed':
                            users = User.query.filter_by(partnership = 'Εργολάβος').all()
                            for user in users:
                                msg = Message('Νέες εργασίες', sender = 'heroku@seaplaellinika.gr', recipients=[user.email])
                                msg.body = 'Έχετε μία νέα ειδοποίηση στο Store To Home'
                                mail.send(msg)
                    
                    return redirect(url_for('notifications'))

    locked_by_engineer = Second_Tier_Partner_Deals.query.filter_by(ad_code = code, partnership = 'Μηχανικός').first()
    locked_by_decorator = Second_Tier_Partner_Deals.query.filter_by(ad_code = code, partnership = 'Διακοσμητής').first()
        
    return render_template('/account/offer.html', locked_by_engineer = locked_by_engineer, locked_by_decorator = locked_by_decorator, current_user = current_user, ad = ad, number = number)


@application.route('/ergolavoi/<code>', methods = ['GET','POST'])
def ergolavoi(code):
    number = UserInterest.query.filter_by(code = code).first()
    ldeal = Last_deal.query.filter_by(ad_code = code).first()
    if request.method == "POST": 
        deal = request.form.get("deal")
        partner_deal = Last_deal(ad_code=code, firstname = current_user.firstname, lastname = current_user.lastname,email=current_user.email,
        partner_number=current_user.phonenumber,partnership=current_user.partnership,
        deal_at=deal,datetime_deal=datetime.now())
        dealbacklog = Deal_Backlog.query.filter_by(code = code).first()
        dealbacklog.firstname_ergolavou = current_user.firstname
        dealbacklog.lastname_ergolavou = current_user.lastname 
        dealbacklog.phonenumber_ergolavou = current_user.phonenumber
        dealbacklog.deal_ergolavou = deal
        dealbacklog.partner_sum = float(dealbacklog.deal_mhxanikou) + float(dealbacklog.deal_diakosmiti) + float(dealbacklog.deal_ergolavou)
        dealbacklog.sell_cost = float(dealbacklog.deal_mhxanikou) + float(dealbacklog.deal_diakosmiti) + float(dealbacklog.deal_ergolavou) + float(dealbacklog.deal_mesiti)
        dealbacklog.bprofit = float(dealbacklog.deal_mhxanikou)*0.06 + float(dealbacklog.deal_diakosmiti)*0.06 + float(dealbacklog.deal_ergolavou)*0.06
        dealbacklog.datetime = datetime.now()
        db.session.add(partner_deal)
        db.session.commit()
        return redirect(url_for('notifications'))
    
    return render_template('/account/ergolavoi.html',ldeal = ldeal, current_user = current_user, number = number)



@application.route('/backlog')
@login_required
def back():
    if current_user.is_admin == 1:
        ads = []
        deals = []
        aggelies = []
        adsbacklog = Ad_Backlog.query.all()
        total = 0

        for ad in adsbacklog:
            ads.append(ad)
        for i in ads:
            deal = Deal_Backlog.query.filter_by(code = i.code).first()
            if deal.bprofit:
                total = total + deal.bprofit
            aggelia = Ad_Backlog.query.filter_by(code = i.code).first()
            if deal:
                deals.append(deal)
                aggelies.append(aggelia)
        print(total)         
    else:
        return 'You are not an admin'
    return render_template('account/backlog.html',deals = deals,aggelies = aggelies,total = total)


@application.route('/team')
def team():
    return render_template('team.html')


@application.route('/FAQ')
def faqs():
    return render_template('FAQ.html')

@application.route('/contact_form', methods = ['GET', 'POST'])
def contact_form(): 
    if request.method == "POST":
        email = request.form.get('email')
        fname = request.form.get('firstName')     
        lname = request.form.get('lastName')  
        region = request.form.get('country')
        description = request.form.get('description')

        print(email)
        print(fname)
        print(lname)
        print(region)
        print(description)

        msg = Message('Νέο μήνυμα', sender = 'heroku@seaplaellinika.gr', recipients=['heroku@seaplaellinika.gr'])
        msg.body = '{} Στάλθηκε από: {} {} <br> Email: {} <br> Περιοχή: {}'.format(description, fname, lname, email, region)
        mail.send(msg)
        return 'Email Sent'
    return render_template('contact_form.html')



@application.route('/popup')
def popup():
    adphoto = Ad.query.all()
    return render_template('popup.html', adphoto = adphoto)





@application.route('/userads', methods = ['GET', 'POST'])
def userads():
    if current_user.is_authenticated:
        ads = Ad.query.filter_by(email=current_user.email).all()

        total_ads = []
        for ad in ads:
            total_ads.append(ad)

    else:
        return redirect(url_for('aggelies'))
    
    return render_template('account/userads.html', total_ads = total_ads)


@application.route('/edit/<code>', methods = ['GET', 'POST'])
def edit(code):

    aggelies = Ad.query.all()
    images = []
    pic_names = []
    check = Ad.query.filter_by(code = code).first()
    
    if current_user.username == check.username:
        file_names=os.listdir('./static/pics/')
        images.append(file_names)

        fordelete = Deal_Backlog.query.filter_by(code = code).first()
        pic_array = Ad.query.filter_by(code = code).first()
        for pic in pic_array.photo:
            print(pic)
        print(len(pic_array.photo))
        
        pictures = Pictures.query.all()
        pic_folder = []

        for picture in pictures:
            if picture.adcode == code:
                pic_folder.append(picture.filename)

        


        for aggelia in aggelies:
            if code in aggelia.code:
                adusername = aggelia.username
                adtitle = aggelia.title
                addescription = aggelia.description
                adregion = aggelia.region
                adaddress = aggelia.address
                adcategory = aggelia.category
                adtmprice = aggelia.tmprice
                ademvado = aggelia.emvado
                adrooms = aggelia.rooms
                adfloor = aggelia.floor 
                adyear = aggelia.year
                adheat = aggelia.heat
                adprice = aggelia.price
                photo = aggelia.photo
            
        for i in images:
            for x in i:
                pic_names.append(x)

        if request.method == "POST":
            title = request.form.get('title')
            description = request.form.get('description')
            category = request.form.get('category')        
            tmprice = request.form.get('tmprice')        
            emvado = request.form.get('emvado')        
            rooms = request.form.get('rooms')        
            floor = request.form.get('floor')        
            year = request.form.get('year') 
            heat = request.form.get('heat')        
            price = request.form.get('price')
        

            for aggelia in aggelies:
                if code in aggelia.code:
                
                    aggelia.title = title 
                    aggelia.description = description
                    aggelia.tmprice = tmprice
                    aggelia.emvado = emvado
                    aggelia.rooms = rooms
                    aggelia.floor = floor
                    aggelia.year = year
                    aggelia.heat = heat
                    aggelia.price = price


            db.session.commit()  
            return redirect(url_for('userads'))


    
    return render_template('account/edit.html',code = code, adusername = adusername, addescription = addescription, 
    adregion = adregion,adcategory=adcategory,ademvado=ademvado, adfloor=adfloor, adheat=adheat, adrooms=adrooms, adtmprice = adtmprice,
      adprice=adprice, pic_names = pic_names, photo = photo, fordelete = fordelete , adtitle = adtitle, adaddress = adaddress,
      adyear = adyear, pic_folder = pic_folder)
    



@application.route('/delete/<code>', methods = ['GET', 'POST'])
def delete(code):
    ad = Ad.query.filter_by(code = code).first()
    if request.method == "POST":
        file_names=os.listdir('./static/pics/')
        routes = Ad.query.all()
        for route in routes:
            if code in route.code:
                photo = route.photo
                for file in file_names:
                    if file in photo:
                        os.remove(os.path.join(application.config['UPLOAD_FOLDER'], file))

        tobedeleted = Ad.query.filter_by(code = code).delete()
        db.session.commit()
        
        return redirect(url_for('userads'))
    
    return render_template('account/delete.html',current_user = current_user, ad = ad)



@application.route('/forgot_password', methods = ['GET', 'POST'])
def forgot_password():
    form = ForgotYourPassword()

    if form.validate_on_submit():
        #email=User.query.filter_by(email=form.email.data).first()
        email = request.form['email']
        token = s.dumps(email, salt = 'reset_password')

        usertoken = User.query.filter_by(email = email).first()
        usertoken.token = token
        print(usertoken.token)
        db.session.commit()

        msg = Message('Reset_password', sender = 'heroku@seaplaellinika.gr', recipients=[email])
        link = url_for('reset_password', token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)
        mail.send(msg)
        return 'Reset password request sent to your email!'

    return render_template('forgot_password.html', form = form)



@application.route('/reset_password/<token>',  methods=['GET', 'POST'])
def reset_password(token):
    try:
        if request.method == "POST":
            email = s.loads(token, salt='reset_password', max_age=360)
            password = request.form.get('password')
            print(password)
            user = User.query.filter_by(token = token).first()
            hashed_password = generate_password_hash(password, method = 'sha256')
            print(hashed_password)
            user.password = hashed_password
            db.session.commit()
            return 'Password Updated'
    except SignatureExpired:
        return 'The token expired'
    return render_template('reset_password.html', token = token)





@application.route('/importfromplot', methods=['GET', 'POST'])
def importfromplot():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        token = request.form.get('token')
        encoded_string = '{}:{}'.format(email,password).encode('utf-8')
        base64_bytes = base64.b64encode(encoded_string)
        base64_decoded_bytes = base64_bytes.decode('utf-8')
        headers = { 'Authorization' : 'Basic ' + base64_decoded_bytes, 'Access-Token' : token }
        url_base = 'https://plot.gr/'
        request_url = url_base + 'api/v2.0/classifieds/my'
        response = requests.get(request_url, headers = headers)
        dat = response.json()
        photo_arr = []
        
        
        

        url = "https://plot.gr/"
        for i in dat['data']['results']['classifieds'].items():
            x = i[1]
        for y in x:
            #t = y
            fullurl = url+str(y['id'])
            page = requests.get(fullurl)
            if y['info']['states']['is_hidden'] == False:
                category = y['info']['base_category']['human_name']
                if category == 'Store':

                    soup = BeautifulSoup(page.content, 'html.parser')
                    h1 = soup.find('h1', class_="classified-title")
                    print(h1.text)
                    

                    address = y['field_values']['address']
                    floor_num = y['field_values']['floor'][0]
                    ppsm = y['field_values']['price_per_square_meter']
                    price = y['field_values']['price']
                    year = y['field_values']['year_of_construction']
                    em = price / ppsm
                    #heat_num = ['field_values']['heat_medium'][0];
                    emvado = round(em)
                    ar_aggelias = y['id']
                    desc = y['field_values']['description']['el']
                    print(ar_aggelias)
                    print(address)
                    print(ppsm)
                    print(price)
                    print(category)
                    print(emvado)
                    if year != None:
                        print(year)
                    else:
                        print('Επικοινωνήστε για περαιτέρω πληροφορίες')

                    if floor_num == '-1':
                        floor = 'Υπόγειο'
                        print(floor)
                    elif floor_num == '0':
                        floor = 'Ισόγειο'
                        print(floor)
                    elif floor_num == '1':
                        floor = '1ος'
                        print(floor)
                    elif floor_num == '2':
                        floor = '2ος'
                        print(floor)
                    elif floor_num == '3':
                        floor = '3ος'
                        print(floor)
                    elif floor_num == '4':
                        floor = '4ος'
                        print(floor)
                    elif floor_num == '5':
                        floor = '5ος'
                        print(floor)
                    elif floor_num == '6':
                        floor = '6ος'
                        print(floor)

                    if 'thessaloniki' or 'Thessaloniki' or 'THESSALONIKI' or 'THESSALONIKH' or 'thessalonikh' or 'Thessalonikh' or 'ΘΕΣΣΑΛΟΝΙΚΗ' or 'Θεσσαλονικη' or 'Θεσσαλονίκη' or 'ΘΕΣΣΑΛΟΝΊΚΗ' in address:
                        city = 'Θεσσαλονίκη'
                    elif 'athina' or 'Athina' or 'Athens' or 'ATHINA' or 'ATHENS' or 'athens' or 'Αθήνα' or 'ΑΘΉΝΑ' or 'ΑΘΗΝΑ' or 'αθηνα' or 'αθήνα' in address:
                        city = 'Αθήνα'
                    else:
                        city = 'Δεν βρέθηκε περιοχή. Παρακαλώ επεξεργαστείτε την αγγελία.'
                    print(city)

                    print(desc)

                    photos = y['field_values']['photos']['native']['values']
                    photos_aggelias = []
                    
                    
                    

                            
                    aggelia = Ad.query.filter_by(code = ar_aggelias).first()
                    if aggelia:
                        print('h aggelia uparxei')
                    else:    
                        for i in photos:
                            photos_aggelias.append(i['files']['size_z'])
                            pic = Pictures(adcode = ar_aggelias, filename = i['files']['size_z'])
                            db.session.add(pic)
                            db.session.commit()
                            if '_0'in i['files']['size_z']:
                                frontpic = i['files']['size_z']
                    
                        fotografies = json.dumps(photos_aggelias)
                        ad = Ad(code = ar_aggelias,firstname = current_user.firstname, lastname = current_user.lastname,username = current_user.username, email = current_user.email,partnership = current_user.partnership, title = h1.text, region = city, address = address, category = category, tmprice = ppsm, emvado = emvado, floor = floor, year = year, price = price, description = desc, pic = frontpic,  photo = fotografies)
                        db.session.add(ad)
                        db.session.commit()
                    
        
        fotos = Pictures.query.all()
        return redirect(url_for('myAccount'))
        #return render_template('aggelies.html', dat = dat, photo_arr = photo_arr, aggelies = aggelies, fotos = fotos )
    return render_template('importfromplot.html')


if __name__ == '__main__':
    application.run(debug=True)

