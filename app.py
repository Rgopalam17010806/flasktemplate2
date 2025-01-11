from flask import flash, redirect, render_template, url_for
from flask_login import login_user, logout_user
from config import app, db, bcrypt, login_manager
from dbmodels import User
from formmodels import Login, Register

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    registerform = Register()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('login unsuccessful', 'danger')
    return render_template('login.html', form=form, registerform=registerform)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = Register()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, False)
        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)