"""Seed file to make sample data for users db."""

from models import User, Post, Tag, PostTag, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()

# Add users
doug = User(first_name='Doug', last_name="Hooker")
kaily = User(first_name='Kaily', last_name="Redacted")
frank = User(first_name='Frank', last_name="Falaffle")
bill = User(first_name='Bill', last_name="Billiams")
leslie = User(first_name='Leslie', last_name="Knope")

# Add posts
p1 = Post(title='Hello World!', content="Man I'm really doing it!'", user_id=1)
p2 = Post(title='Pawnee is great!', content='Everyone should live here!', user_id=5)
p3 = Post(title="Hey I'm Frank", content='I met Sly Stallone once.', user_id=3)
p4 = Post(title='Stop emailing me', content="I can't stand it!!!", user_id=4)
p5 = Post(title='Ann', content='Oh Ann, you beautiful opalescent tree shark.', user_id=5)
p6 = Post(title='Calzones are an abomination', content='Seriously Ben, stop talking about them.', user_id=5)

# Add tags
t1 = Tag(name='cool')
t2 = Tag(name='fun')
t3 = Tag(name='boring')

# Add post_tags
pt1 = PostTag(post_id=4, tag_id=2)
pt2 = PostTag(post_id=4, tag_id=1)
pt3 = PostTag(post_id=1, tag_id=2)
pt4 = PostTag(post_id=5, tag_id=2)
pt5 = PostTag(post_id=6, tag_id=1)
pt6 = PostTag(post_id=3, tag_id=3)

# Add new users to session, so they'll persist
db.session.add_all([doug, kaily, frank, bill, leslie])

# Commit--otherwise, this never gets saved!
db.session.commit()

# Add new posts to session, so they'll persist
db.session.add_all([p1,p2,p3,p4,p5,p6])

# Commit--otherwise, this never gets saved!
db.session.commit()

# Add new tags to session, so they'll persist
db.session.add_all([t1, t2, t3])

# Commit--otherwise, this never gets saved!
db.session.commit()

# Add new post_tags to session, so they'll persist
db.session.add_all([pt1,pt2,pt3,pt4,pt5,pt6])

# Commit--otherwise, this never gets saved!
db.session.commit()