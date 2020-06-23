# import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import datetime

# intialize a variable for our DB by running SQLAlchemy. db is standard name
db = SQLAlchemy()

class User(db.Model):
    """User Model"""
    __tablename__ = 'users'

    # default img_url for inserts / updates
    url = 'https://www.pngkey.com/png/full/115-1150152_default-profile-picture-avatar-png-green.png'

    # define the columns of the table / nullable is True by default / default values only work if used by this model
    # if you try to add something to the db direcly using SQL the default is not there
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False) 
    img_url = db.Column(db.Text, default=url)

    posts = db.relationship('Post', backref='user', cascade='all, delete-orphan')

    @property
    def full_name(self):
        """Return full name of user."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def order_by_last_name(cls):
        """Orders list results by last_name DESC, then first_name."""
        return cls.query.order_by(User.last_name.desc(), User.first_name).all()

    def __repr__(self):
        """Show info about user"""

        u = self
        return f"<User id={u.id} first name={u.first_name} last_name={u.last_name}>"

class Post(db.Model):
    """Post Model"""
    __tablename__ = 'posts'

    # define the columns of the table / nullable is True by default / default values only work if used by this model
    # if you try to add something to the db direcly using SQL the default is not there
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    tags = db.relationship('Tag', secondary='post_tags', backref='posts') 

    @property
    def friendly_date(self):
        """Return nicely-formatted date."""

        return self.created_at.strftime("%a %b %d  %Y, %I:%M %p")

    def __repr__(self):
        """Show info about user"""

        p = self
        return f"<User id={p.user_id} title={p.title} created_at={p.created_at}>"

class Tag(db.Model):
    """Tag Model"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    @classmethod
    def get_ids(cls):
        """Get all tag ids"""

        return cls.query.order_by(Tag.id).all()

    def __repr__(self):
        """Show info about tag"""

        t = self
        return f"<Tag name={t.name}>"

class PostTag(db.Model):
    """PostTag Model"""
    __tablename__ = 'post_tags'

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

    # def __repr__(self):
    #     """Show info about post_tag"""

    #     t = self
    #     return f"<Tag name={t.name}>"

# associate Flask app and connect with our DB
def connect_db(app):
    db.app = app
    db.init_app(app)