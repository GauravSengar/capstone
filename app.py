from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user,login_required
from hashlib import sha256
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
import os.path as op
import re
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'randomSECERETY'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

admin = Admin(app)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(256))
    password = db.Column(db.String(512))

class Course(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(150))
    description = db.Column(db.String(50))
    author = db.Column(db.String(50))
    image_name = db.Column(db.String(200))




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        courses = Course.query.all()
        return render_template('index.html',current_user=current_user,courses=courses)
    return render_template('index.html',current_user=current_user)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email = email).first()
        if user:
            if user.password == sha256(password.encode()).hexdigest():
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid Password')
                return redirect(url_for('login'))
        else:
            flash("User Doesn't exist")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        conf_pass = request.form['confirm_password']
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if not re.search(regex,email):
            flash('Invalid email')
            return redirect(url_for('register'))

        if password != conf_pass:
            flash('Password is not same as Confirm Password')
            return redirect(url_for('register'))
        else:
            user = User(email=email,password=sha256(password.encode()).hexdigest())
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

class MedemyAdminView(ModelView):
    def is_accessible(self):
        admins_list=['harsh@gmail.com']
        if current_user.is_authenticated and (current_user.email in admins_list):
            return True
        else:
            return False

class MedemyFileView(FileAdmin):
    def is_accessible(self):
        admins_list=['harsh@gmail.com']
        if current_user.is_authenticated and (current_user.email in admins_list):
            return True
        else:
            return False

admin.add_view(MedemyAdminView(Course,db.session))

path = op.join(op.dirname(__file__), 'static')
admin.add_view(MedemyFileView(path, '/static/', name='Static'))

if __name__ == "__main__":
    app.run(debug=True)
