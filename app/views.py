from app import app
import os
from flask import abort, \
                  flash, \
                  redirect, \
                  render_template, \
                  request, \
                  session, \
                  url_for
from flask.ext.login import current_user, \
                            login_user, \
                            logout_user, \
                            login_required
from .forms import LoginForm, \
                   UserForm
from .database import find_user_by_name, \
                      find_files_all, \
                      find_file_by_id, \
                      find_user_by_id,\
                      find_user_all,\
                      db, \
                      File, \
                      User
import json
import base64
import md5
import random
import hmac
import hashlib
from datetime import timedelta
from url_decode import urldecode

@app.route('/', methods=['GET'])
def home():
    if not current_user.is_authenticated() and app.config['FILES_PROTECTED']:
        return redirect(url_for('login'))

    """ Home page """
    if request.args.get('q'):
        search_query = request.args.get('q')
    else:
        search_query = ""

    return render_template('index.html', q=search_query)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login page """
    if current_user.is_authenticated():
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = find_user_by_name(form.username.data)
        if user is None or not user.is_valid_password(form.password.data):
            flash('Invalid username or password', 'danger')
        elif login_user(user, remember=form.remember.data):
            # Enable session expiration only if user hasn't chosen to be remembered.
            session.permanent = not form.remember.data
            return redirect(request.args.get('next') or url_for('home'))
    elif form.errors:
        flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """ Logout the user """
    logout_user()
    return redirect(url_for('login'))


@app.route('/user/list/', methods=['GET'])
@login_required
def user_list():
    """ List all users """
    if not current_user.role == "admin":
        abort(404)

    users = find_user_all()

    return render_template('user_list.html',
        users=users,
        page_title="Users"
    )

@app.route('/user/add/', methods=['GET', 'POST'])
@login_required
def user_create():
    """ Create a user """
    if not current_user.role == "admin":
        abort(404)

    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(
            name = form.name.data,
            password = form.password.data,
            role = form.role.data
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('user_list'))

    return render_template('user_create.html',
        form=form,
        page_title="Create a User",
        form_action=url_for('user_create'),
        form_submit_button_title="Create"
    )

@app.route('/user/update/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_update(user_id):
    """ Update a user """
    if not current_user.role == "admin":
        abort(404)

    user = find_user_by_id(user_id)
    if not user:
        abort(404)

    form = UserForm(obj=user)
    del form.password
    if request.method == 'POST' and form.validate_on_submit():
        user.name = form.name.data
        user.role = form.role.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('user_list'))

    return render_template('user_update.html',
        user=user,
        form=form,
        page_title="Update %s" % user.name ,
        form_action=url_for('user_update', user_id=user.id),
        form_submit_button_title="Update"
    )

@app.route('/user/delete/<int:user_id>', methods=['GET'])
@login_required
def user_delete(user_id):
    """ Delete a user """
    if not current_user.role == "admin":
        abort(404)

    user = find_user_by_id(user_id)
    if not user:
        abort(404)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('user_list'))


@app.route('/change-password/', methods=['GET', 'POST'])
@login_required
def user_change_password():
    """ Change a user's password """

    # Is this an admin resetting a user's password?
    if request.args.get('user_id'):
        user_id = request.args.get('user_id')

        if user_id != current_user.id and not current_user.role == "admin":
            abort(404)
    else:
        user_id = current_user.id

    user = find_user_by_id(user_id)
    if not user:
        abort(404)

    form = UserForm(obj=user)
    del form.name
    del form.role
    if request.method == 'POST' and form.validate_on_submit():
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('user_change_password', user_id=user.id))

    if current_user.role == "admin":
        page_title = "Change password for %s" % user.name
    else:
        page_title = "Change your Password"

    return render_template('user_change_password.html',
        user=user,
        form=form,
        page_title=page_title,
        form_action=url_for('user_change_password', user_id=user.id),
        form_submit_button_title="Change"
    )

@app.route('/upload/')
@login_required
def files_upload():
    """ Upload files """
    s3_success_action_status = '201'
    s3_acl = "public-read"
    folder = md5.new("%032x" % random.getrandbits(128)).hexdigest()
    folder_path = "%s/" % folder
    s3_policy = {
        "expiration": "2038-01-01T00:00:00Z",
        "conditions": [
            {"bucket": app.config['AWS_S3_BUCKET']},
            ["starts-with", "$key", folder_path],
            {"acl": s3_acl},
            {"success_action_status": s3_success_action_status},
            ["content-length-range", 0, app.config['MAX_UPLOAD_SIZE']]
        ]
    }

    policy = base64.b64encode(json.dumps(s3_policy))
    signature = base64.b64encode(hmac.new(app.config['AWS_SECRET_ACCESS_KEY'], policy, hashlib.sha1).digest())

    return render_template('upload.html',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        s3_acl=s3_acl,
        s3_bucket=app.config['AWS_S3_BUCKET'],
        s3_folder=folder_path,
        s3_policy=policy,
        s3_signature=signature,
        page_title="Upload",
        folder=folder,
        s3_success_action_status=s3_success_action_status,
        max_upload_size=app.config['MAX_UPLOAD_SIZE']
    )


@app.route('/rest/file/', methods=['GET'])
def file_index():
    if not current_user.is_authenticated() and app.config['FILES_PROTECTED']:
        return redirect(url_for('login'))

    """ List all files """
    if not request.args.get('page'):
        abort(500)
    page_num = int(request.args.get('page'))

    if request.args.get('q'):
        search_query = request.args.get('q')
    else:
        search_query = None

    limit = 50
    offset = (page_num - 1) * limit
    files = find_files_all(offset=offset, limit=limit, search_query=search_query)

    response = []
    for file in files:
        response.append(file.to_object())

    return app.response_class(response=json.dumps(response), mimetype='application/json')


@app.route('/rest/file/', methods=['POST'])
@login_required
def file_add():
    """ Add a file """
    file = File(
        name=urldecode(request.form['name']),
        folder=request.form['folder'],
        size=int(request.form['size']),
        owner_id=int(current_user.id)
    )
    db.session.add(file)
    db.session.commit()

    return app.response_class(response=json.dumps(file.to_object()), mimetype='application/json')


@app.route('/rest/file/<int:file_id>', methods=['DELETE'])
@login_required
def file_delete(file_id):
    """ Delete a file """
    file = find_file_by_id(file_id)
    if not file:
        abort(404)

    # Delete the file from S3
    file.delete()

    # Remove the file from the database
    db.session.delete(file)
    db.session.commit()

    return app.response_class(response=json.dumps(file.to_object()), mimetype='application/json')
