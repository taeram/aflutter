from app import app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, prompt_bool, prompt
from flask.ext.login import UserMixin
from flask.ext.migrate import Migrate, MigrateCommand
import pytz
from datetime import datetime
from .snippets.hash_passwords import check_hash, make_hash
from hashlib import sha1
from .auth import login_serializer
import md5
import random
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from urllib import unquote
from .helpers import delete_file

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(usage="Manage the database")
manager.add_command('migrate', MigrateCommand)


@manager.command
def create():
    """ Create the database """
    db.create_all()
    setup()


@manager.command
def setup():
    """ Populate the database with some defaults """
    if prompt_bool("Do you want to add an admin user?"):
        name = prompt("Username for admin")
        password = prompt("Password for admin")
        user = User(name=name, password=password, role="admin")
        db.session.add(user)
        db.session.commit()


@manager.command
def drop():
    """ Empty the database """
    if prompt_bool("Are you sure you want to drop all tables from the database?"):
        db.drop_all()


@manager.command
def recreate():
    """ Recreate the database """
    drop()
    create()


def find_user_all(offset=None, limit=None):
    """ Get all users """
    query = db.session.query(User).\
                order_by(db.desc(User.name))

    if offset is not None and limit is not None:
        query = query.limit(limit).\
                      offset(offset)

    return query.all()


def find_user_by_id(user_id):
    """ Get a user by id """
    try:
        return db.session.query(User).\
                         filter(User.id == user_id).\
                         one()
    except NoResultFound:
        return None


def find_user_by_name(name):
    """ Get a user by name """
    try:
        return db.session.query(User).\
                         filter(User.name == name).\
                         one()
    except NoResultFound:
        return None


def find_files_all(offset, limit, search_query):
    """ Get all galleries """
    query = db.session.query(File)

    if search_query is not None:
        query = query.filter(func.lower(File.name).like('%%%s%%' % search_query))

    return query.order_by(db.desc(File.created)).\
                limit(limit).\
                offset(offset).\
                all()


def find_file_by_id(file_id):
    """ Find a single file """
    try:
        return db.session.query(File).\
                         filter(File.id == file_id).\
                         one()
    except NoResultFound:
        return None


class User(db.Model, UserMixin):

    """ A user """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False, default="user")

    def __init__(self, name, password, role):
        """ Setup the class """
        self.name = name
        self.password = make_hash(password)
        self.role = role

    def get_role(self):
        return self.role

    def set_role(self, role):
        self.role = role
        return self

    def set_password(self, password):
        self.password = make_hash(password)

    def get_auth_token(self):
        """ Get an auth token. Used when "remember me" is checked on login """
        data = (self.id, sha1(self.password).hexdigest())
        return login_serializer.dumps(data)

    def is_valid_password(self, password):
        """Check if provided password is valid."""
        return check_hash(password, self.password)


class File(db.Model):

    """ A file """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    size = db.Column(db.Integer, nullable=False)
    folder = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime(timezone=True))

    def __init__(self, name, folder, size, owner_id):
        """ Setup the class """
        self.name = name
        self.folder = folder
        self.size = size
        self.owner_id = owner_id
        self.created = datetime.utcnow()

    def delete(self):
        """ Delete a file """
        return delete_file(self.folder, self.name)

    def to_object(self):
        """ Get it as an object """
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "folder": self.folder,
            "created": self.created.strftime('%Y-%m-%d %H:%M:%S +0000')
        }

