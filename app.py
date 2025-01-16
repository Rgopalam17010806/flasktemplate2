import random
import string
from flask_mail import Message
from flask_mail import Mail
from config import bcrypt, login_manager, app, db, mail
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask_cors import CORS
from models import ForgotPasswordForm, Login, Register, ResetPasswordForm, User
from werkzeug.security import generate_password_hash, check_password_hash 


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

# Route to request password reset
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()  # Assume this form asks for the user's email
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate a reset token
            token = user.get_reset_token()
            # Correctly generate the reset URL with the token (passing token as a keyword argument)
            reset_url = url_for('reset_password', token=token, _external=True)
            # Send the email (using Flask-Mail)
            msg = Message("Password Reset Request", recipients=[user.email])
            msg.body = f"To reset your password, visit the following link: {reset_url}"
            mail.send(msg)
            flash('A password reset link has been sent to your email address.', 'info')
        else:
            flash('No account with that email exists.', 'warning')
    return render_template('forgot_password.html', form=form)


# Route to reset the password
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()  # Form for resetting password
    user = User.verify_reset_token(token)  # Verify the token (this method should be in your User model)

    if not user:  # If the token is invalid or expired
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('home'))  # Redirect to home page or any other page you prefer

    if request.method == 'POST' and form.validate_on_submit():
        new_password = form.password.data
        confirm_password = form.confirm_password.data
        
        if new_password != confirm_password:  # Check if both passwords match
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password', token=token))

        user.set_password(new_password)  # Set the new password (you should have this method in your User model)
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))  # Redirect to the login page after successful reset

    return render_template('reset_password.html', form=form, token=token)


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