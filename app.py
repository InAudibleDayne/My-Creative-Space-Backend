import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import SET, DATETIME

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://master:Pokemon.Master151@localhost:3306/my_creative_space?auth_plugin=mysql_native_password'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(45), unique=True)
  name = db.Column(db.String(45))

  def __init__(self, username, name):
    self.username = username
    self.name = name

class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'username', 'name')

class Blogs(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(45), unique=False)
  description = db.Column(db.String(160), unique=False)
  blog_type = db.Column(db.String(8), unique=False)
  file_location = db.Column(db.String(160), unique=False)
  file_blob = db.Column(db.LargeBinary, unique=False)
  created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)
  
  def __init__(self, title, description, blog_type, file_location, file_blob, created_by_id):
    self.title = title
    self.description = description
    self.blog_type = blog_type
    self.file_location = file_location
    self.file_blob = file_blob
    self.created_by_id = created_by_id

class BlogSchema(ma.Schema):
  class Meta:
    fields = ('id', 'title', 'description', 'blog_type', 'file_location', 'file_blob', 'created_by_id')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)

@app.route('/user', methods=["POST"])
def add_user():
  username = request.json['username']
  name = request.json['name']

  existingcheck = Users.query.filter_by(username=username).all()

  if existingcheck == []:
    new_user = Users(username, name)

    db.session.add(new_user)
    db.session.commit()

    user = Users.query.get(new_user.id)

    return user_schema.jsonify(user)

  else:
    user = users_schema.dump(existingcheck)
    result = user.pop()
    return jsonify(result)

@app.route('/user/<id>', methods=["GET"])
def get_user(id):
  user = Users.query.get(id)
  return user_schema.jsonify(user)

@app.route('/user/<id>', methods=["PUT"])
def update_user(id):
  user = Users.query.get(id)
  username = request.json['username']
  name = request.json['name']

  user.username = username
  user.name = name

  db.session.commit()
  return user_schema.jsonify(user)

@app.route('/user/<id>', methods=["DELETE"])
def delete_user(id):
  user = Users.query.get(id)
  db.session.delete(user)
  db.session.commit()

  return "User has been deleted."

@app.route('/users', methods=["GET"])
def get_users():
  all_users = Users.query.all()
  result = users_schema.dump(all_users)

  return jsonify(result)

@app.route('/blog', methods=["POST"])
def add_blog():
  title = request.json['title']
  description = request.json['description']
  blog_type = request.json['blog_type']
  file_location = request.json['file_location']
  file_blob = str.encode(request.json['file_blob'])
  created_by_id = request.json['created_by']

  print(file_blob)

  new_blog = Blogs(title, description, blog_type, file_location, file_blob, created_by_id)

  db.session.add(new_blog)
  db.session.commit()

  blog = Blogs.query.get(new_blog.id)

  return blog_schema.jsonify(blog)

@app.route('/blogs', methods=["GET"])
def get_recent_blogs():
  newest_blogs = Blogs.query.order_by(Blogs.id.desc()).limit(10).all()
  result = blogs_schema.dump(newest_blogs)

  return jsonify(result)

@app.route('/blogs/<offset>', methods=["GET"])
def get_next_blogs(offset):
  next_blogs = Blogs.query.order_by(Blogs.id.desc()).limit(10).offset(offset).all()
  result = blogs_schema.dump(next_blogs)

  return jsonify(result)

@app.route('/blogs/user/<id>/<offset>', methods=["GET"])
def get_blogs_by_user(id, offset):
  blogs = Blogs.query.filter_by(created_by_id=f'{id}').order_by(Blogs.id.desc()).limit(10).offset(offset).all()
  result = blogs_schema.dump(blogs)

  return jsonify(result)

@app.route('/blogs/user/<id>/<category>/<offset>')
def get_blogs_by_category_and_user(id, category, offset):
  blogs = Blogs.query.filter_by(blog_type=f'{category}', created_by_id=f'{id}').order_by(Blogs.id.desc()).limit(10).offset(offset).all()
  result = blogs_schema.dump(blogs)

  return jsonify(result)

@app.route('/blogs/sort/<category>', methods=["GET"])
def get_blogs_by_category(category):
  blogs = Blogs.query.filter_by(blog_type=f'{category}').order_by(Blogs.id.desc()).limit(10).all()
  result = blogs_schema.dump(blogs)

  return jsonify(result)

@app.route('/blogs/sort/<category>/<offset>', methods=["GET"])
def get_next_blogs_by_category(category, offset):
  blogs = Blogs.query.filter_by(blog_type=f'{category}').order_by(Blogs.id.desc()).limit(10).offset(offset).all()
  result = blogs_schema.dump(blogs)

  return jsonify(result)


@app.route('/blog/<id>', methods=["GET"])
def get_blog(id):
  blog = Blogs.query.get(id)
  return blog_schema.jsonify(blog)

@app.route('/blog/<id>', methods=["PUT"])
def update_blog(id):
  blog = Blogs.query.get(id)

  title = request.json['title']
  description = request.json['description']
  blog_type = request.json['blog_type']
  file_location = request.json['file_location']
  file_blob = str.encode(request.json['file_blob'])
  created_by_id = request.json['created_by']

  blog.title = title
  blog.description = description
  blog.blog_type = blog_type
  blog.file_location = file_location
  blog.file_blob = file_blob
  blog.created_by_id = created_by_id

  db.session.commit()
  return blog_schema.jsonify(blog)
  
@app.route('/blog/<id>', methods=["DELETE"])
def delete_blog(id):
  blog = Blogs.query.get(id)
  db.session.delete(blog)
  db.session.commit()
  
  return "Blog item successfully deleted."

@app.route('/blogs/search/<keywords>/<offset>', methods=["GET"])
def get_blogs_by_search_params(keywords, offset):
  blogs = Blogs.query.filter(Blogs.title.like("%" + keywords + "%")).order_by(Blogs.id.desc()).limit(10).offset(offset).all()
  result = blogs_schema.dump(blogs)

  return jsonify(result)

@app.route('/blogs/usersearch/<id>/<keywords>/<offset>', methods=["GET"])
def get_blogs_by_search_params_for_user(id, keywords, offset):
  blogs = Blogs.query.filter_by(created_by_id=f'{id}').filter(Blogs.title.like("%" + keywords + "%")).order_by(Blogs.id.desc()).limit(10).offset(offset).all()
  result = blogs_schema.dump(blogs)

  return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)