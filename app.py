# import Flask and any libraries you want to use
from flask import Flask, request, render_template, redirect, flash
# get DB related stuff from models.py
from models import db, connect_db, User, Post, Tag, PostTag

# instantiate and instance of Flask. app is standard name
app = Flask(__name__)

# specify which RDBMS you're using (i.e. postgresql) and name of DB you want app to use. "postgresql://ownername:yourpassword@localhost/databasename" OR "postgresql:///databasename"
# must do before you associate to your app or else it will error out
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///unit23_db"
# remove track modifications warning at startup
app.config["SQLALCHEMY_TRACKMODIFICATIONS"] = False
# print all SQL statements to terminal (helpful in debugging and learning the ORM method calls)
app.config["SQLALCHEMY_ECHO"] = True

# connect to db
connect_db(app)

# import debug toolbar
from flask_debugtoolbar import DebugToolbarExtension
# required by debugtoolbar for debugging session
app.config["SECRET_KEY"] = "secret"
# makes sure redirects aren't stopped by the debugtoolbar
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# instantiate class on our app
debug = DebugToolbarExtension(app)

# default url for inserts / updates
url = 'https://www.pngkey.com/png/full/115-1150152_default-profile-picture-avatar-png-green.png'

@app.route("/")
def root():
    """Show recent list of posts, most-recent first."""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("homepage.html", posts=posts)

################### USERS ROUTES ############################

@app.route("/users")
def list_users():
    """List users and show link to add user form."""

    users = User.order_by_last_name()
    return render_template("user_list.html", users=users)

@app.route("/users/new")
def get_user_form():
    """Get new user form."""

    return render_template("new_user_form.html")

@app.route("/users/new", methods=["POST"])
def add_user():
    """Add user to db and redirect to user list."""

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    img_url = request.form['img_url']
    img_url = img_url if img_url else url

    if first_name and last_name:
        user = User(first_name=first_name, last_name=last_name, img_url=img_url)
        db.session.add(user)
        db.session.commit()

        flash(f"User successfully added.", "success")
        return redirect("/users")
    else:
        flash(f"Must have first and last name. Changes not saved.", "error")
        return redirect("/users/new")

@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Show info on a single user."""

    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    return render_template("user_details.html", user=user, posts=posts)

@app.route("/users/<int:user_id>/edit")
def get_edit_user_form(user_id):
    """Get info on a single user for edit form."""

    user = User.query.get_or_404(user_id)
    return render_template("edit_user_form.html", user=user)

@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user(user_id):
    """Edit info on a single user."""

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    img_url = request.form['img_url']
    img_url = img_url if img_url else url

    user = User.query.get_or_404(user_id)
    if first_name and last_name:

        user.first_name = first_name
        user.last_name = last_name
        user.img_url = img_url
        
        db.session.add(user)
        db.session.commit()

        flash(f"Edit successful.", "success")
        return redirect(f"/users/{user_id}")
    else:
        flash(f"Must have first and last name. Changes not saved.", "error")
        return redirect(f"/users/{user_id}")

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Delete user from db."""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User { user.full_name } deleted.", "success")
    return redirect("/users")

@app.route("/users/<int:user_id>/posts/new")
def get_post_form(user_id):
    """Get new post form."""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template("new_post_form.html", user=user, tags=tags)

@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def add_post(user_id):
    """Add post to db and redirect user page."""

    title = request.form['title']
    content = request.form['content']
    tag_ids = [int(num) for num in request.form.getlist("tag_group")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    if title and content:
        post = Post(title=title, content=content, user_id=user_id, tags=tags)
        db.session.add(post)
        db.session.commit()

        flash(f"Post successfully added.", "success")
        return redirect(f"/users/{user_id}")
    else:
        flash(f"Must fill out all fields. Changes not saved.", "error")
        return redirect(f"/users/{user_id}")

################### POSTS ROUTES ############################

@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """Show info on a single post."""

    post = Post.query.get_or_404(post_id)
    return render_template("post_details.html", post=post)

@app.route("/posts/<int:post_id>/edit")
def get_edit_post_form(post_id):
    """Get info on a single post for edit form."""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template("edit_post_form.html", post=post, tags=tags)

@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post(post_id):
    """Edit info on a single post."""

    post = Post.query.get_or_404(post_id)
    title = request.form['title']
    content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist("tag_group")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    # to show which tags are already on post
    tags = db.session.query(Tag.id).all()

    if title and content:

        post.title = title
        post.content = content
        
        db.session.add(post)
        db.session.commit()

        flash(f"Post edited successfully.", "success")
        return redirect(f"/users/{post.user.id}")
    else:
        flash(f"Must fill out all fields. Changes not saved.", "error")
        return redirect(f"/users/{post.user.id}")

@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """Delete post from db."""

    # get post so that we can get the user.id because once the post is deleted we cannot use post.user.id in return clause
    post = Post.query.get_or_404(post_id)
    # save user.id to variable
    id = post.user.id
    # find post and delete
    db.session.delete(post)
    # commit delete statement
    db.session.commit()

    flash(f"Post deleted.", "success")
    return redirect(f"/users/{id}")

################### TAGS ROUTES ############################

@app.route("/tags")
def list_tags():
    """List tags and show link to add tags form."""

    tags = Tag.query.all()
    return render_template("tag_list.html", tags=tags)

@app.route("/tags/<int:tag_id>")
def show_tag(tag_id):
    """Show info on a single tag."""

    tag = Tag.query.get_or_404(tag_id)
    return render_template("tag_details.html", tag=tag)

@app.route("/tags/new")
def get_tag_form():
    """Get new tag form."""

    posts = Post.query.all()
    return render_template("new_tag_form.html", posts=posts)

@app.route("/tags/new", methods=["POST"])
def add_tag():
    """Add tag to db and redirect to tag list."""

    name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("post_group")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()

    if name:
        tag = Tag(name=name, posts=posts)
        db.session.add(tag)
        db.session.commit()

        flash(f"Tag successfully added.", "success")
        return redirect("/tags")
    else:
        flash(f"Must have a name for the Tag. Changes not saved.", "error")
        return redirect("/tags/new")

@app.route("/tags/<int:tag_id>/edit")
def get_edit_tag_form(tag_id):
    """Get info on a single tag for edit form."""

    posts = Post.query.all()
    tag = Tag.query.get_or_404(tag_id)
    return render_template("edit_tag_form.html", tag=tag, posts=posts)

@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def edit_tag(tag_id):
    """Edit info on a single tag."""

    tag = Tag.query.get_or_404(tag_id)

    name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("post_group")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    
    if name:

        tag.name = name
        
        db.session.add(tag)
        db.session.commit()

        flash(f"Tag edited successfully.", "success")
        return redirect(f"/tags")
    else:
        flash(f"Must fill out all fields. Changes not saved.", "error")
        return redirect(f"/tags/{tag.id}/edit")

@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """Delete tag from db."""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"{ tag.name } deleted.", "success")
    return redirect("/tags")

    flash(f"{tag.name} deleted.", "success")
    return redirect(f"/tags")