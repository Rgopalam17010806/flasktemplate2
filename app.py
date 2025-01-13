from config import bcrypt, login_manager, app, db
from flask import Flask, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask_cors import CORS
from models import Login, Register, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Flask Routes
#index
@app.route('/')
def index():
    return render_template('home.html')

#home
@app.route('/home')
def home():
    return render_template('home.html')


#login
@app.route('/login', methods=['GET','POST'])
def login():
    form = Login()
    registerform = Register()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('login successful','success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password','danger')
    return render_template('login.html', form=form, registerform=registerform)


#registration
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = Register()

    if form.validate_on_submit():
        # Hashing the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Creating a new user instance with the hashed password
        new_user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            password=hashed_password  # Store the hashed password here
        )
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log the user in after registration
        login_user(new_user)

        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    return render_template('home.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)