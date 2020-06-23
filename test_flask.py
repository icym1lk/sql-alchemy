from unittest import TestCase

from app import app
from models import db, User, Post

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_db'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Add sample user."""

        # User.query.delete()
        # # Post.query.delete()

        doug = User(first_name='Doug', last_name="Hooker")
        # p1 = Post(title='Hello World!', content='Man I"m really doing it!', user_id=1)
        db.session.add(doug)
        db.session.commit()
        # db.session.add(p1)
        # db.session.commit()

        self.user_id = doug.id
        self.user = doug
        # self.post_id = p1.id
        # self.post = p1

    def tearDown(self):
        """Clean up any fouled transaction."""

        Post.query.delete()
        User.query.delete()
        
        # db.session.rollback()

    def test_homepage(self):
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Blogly Recent Posts</h1>', html)

    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)

    def test_show_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2>Posts</h2>', html)
            self.assertIn(self.user.last_name, html)

    def test_add_user_success(self):
        with app.test_client() as client:
            d = {"first_name": "John Q", "last_name": "Test", "img_url": ""}
            resp = client.post("/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("User successfully added.", html)
    
    def test_add_user_fail(self):
        with app.test_client() as client:
            d = {"first_name": "", "last_name": "Test", "img_url": ""}
            resp = client.post("/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Must have first and last name. Changes not saved.", html)

    def test_show_edit_user_form(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>Edit { self.user.full_name } details</h1>', html)

    def test_edit_user_success(self):
        with app.test_client() as client:
            d = {"first_name": "John Q", "last_name": "Test", "img_url": ""}
            resp = client.post(f"/users/{self.user_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit successful.", html)
    
    def test_edit_user_fail(self):
        with app.test_client() as client:
            d = {"first_name": "", "last_name": "Test", "img_url": ""}
            resp = client.post(f"/users/{self.user_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Must have first and last name. Changes not saved.", html)

    def test_delete_user(self):
        with app.test_client() as client:
            d = {"first_name": "John Q", "last_name": "Test", "img_url": ""}
            resp = client.post(f"/users/{self.user_id}/delete", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"User { self.user.full_name } deleted.", html)

    def test_show_user_posts(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/posts/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn(f'<p><em>By { self.user.full_name }</em></p>', html)
            self.assertIn(self.user.full_name, html)

    # causes errors for all previous tests which work fine 
    def test_add_user_post_success(self):
        with app.test_client() as client:
            d = {"title": "This is a title", "content": "Content goes here", "created_at": "", "user_id": f"self.user_id"}
            resp = client.post(f"/users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Post successfully added.", html)
    
    def test_add_user_post_fail(self):
        with app.test_client() as client:
            d = {"title": "This is a title", "content": "", "created_at": "", "user_id": f"self.user_id"}
            resp = client.post(f"/users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Must fill out all fields. Changes not saved.", html)

    # AttributeError: 'InstrumentedList' object has no attribute 'post_id'
    def test_show_single_post(self):
        with app.test_client() as client:
            d = {"title": "This is a title", "content": "Content goes here", "created_at": "", "user_id": f"self.user_id"}
            client.post(f"/users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            resp = client.get(f"/posts/{self.user.posts.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1>{ self.post.title }</h1>', html)
            self.assertIn(self.user.last_name, html)

    # AttributeError: 'InstrumentedList' object has no attribute 'post_id'
    # def test_edit_user_post_success(self):
    #     with app.test_client() as client:
    #         d = {"title": "This is a title", "content": "Content goes here", "created_at": "", "user_id": f"self.user_id"}
    #         resp = client.post(f"/posts/{self.user.posts.post_id}/edit", data=d, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Post edited successfully.", html)
    
    # AttributeError: 'InstrumentedList' object has no attribute 'post_id'
    # def test_edit_user_post_fail(self):
    #     with app.test_client() as client:
    #         d = {"title": "This is a title", "content": "", "created_at": "", "user_id": f"self.user_id"}
    #         resp = client.post(f"/posts/{self.user.posts.post_id}/edit", data=d, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Must fill out all fields. Changes not saved.", html)