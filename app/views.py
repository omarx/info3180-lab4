import os

from werkzeug.security import check_password_hash

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required, logout_user
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm, UploadForm


###
# Routing for your application.
###
def get_uploaded_images():
    uploaded_images = []
    rootdir = os.path.join(app.config['UPLOAD_FOLDER'])
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            # Assuming you only want to list images, you might check the file extension here
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                uploaded_images.append(file)
    return uploaded_images


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(filepath)
        flash('File successfully uploaded', 'success')
        return redirect(url_for('home'))  # Adjust the redirect as necessary
    return render_template('upload.html', form=form)


@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)


@app.route('/files')
@login_required
def files():
    image_filenames = get_uploaded_images()
    return render_template('files.html', images=image_filenames)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # Validates the entire form submission
        user = UserProfile.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password,
                                        form.password.data):  # Assuming user.password is the hashed password
            login_user(user)
            flash('You have successfully logged in.', 'success')
            return redirect(url_for('upload'))  # Assuming 'upload' is the endpoint for the upload route
        else:
            flash('Invalid username or password.', 'danger')
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()


###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
