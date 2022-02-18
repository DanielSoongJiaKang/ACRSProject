from flask import Blueprint, render_template, request, flash, redirect, url_for,current_app, jsonify
from .models import User, UserAudit
from . import db
from flask_login import  login_required,  current_user
from functools import wraps
from .models import  Post, Comment, LikePost
from werkzeug.security import generate_password_hash
import pandas as pd
import os
import pytz
from datetime import datetime


userlist = Blueprint('userlist', __name__)

class userlists:
    def __init__(self, emailp, passwordp, rolesp, namep, contactp):
        self.emailp = emailp
        self.passwordp = passwordp
        self.rolesp = rolesp
        self.namep = namep
        self.contactp = contactp


def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", category="warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view



#query on all data
@userlist.route('/userlist')
def list():
    all_data = User.query.order_by(User.id.desc()).all()
    return render_template("userlist.html", user=current_user, users = all_data)

#update users
@userlist.route('/updateuser', methods = ['GET', 'POST'])
def updateuser():
    if request.method == 'POST':
        my_data = User.query.get(request.form.get('id'))


        my_data.email = request.form['email']
        my_data.roles = request.form['roles']
        my_data.name = request.form['name']
        my_data.contact = request.form['contact']
        my_data.status = request.form['status']
        GMT = pytz.timezone('Singapore')
        now = datetime.now(GMT)
        datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
        new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Update in User Management User ID: " + str(my_data.id))
        db.session.add(new_audit)
        db.session.commit()
        flash("User Updated Successfully")

        return redirect(url_for('userlist.list'))

#delete users
@userlist.route('/deleteuser', methods = ['GET', 'POST'])
def deleteuser():
    if request.method == 'POST':
        i = 0
        for getid in request.form.getlist('mycheckbox'):
            db.session.execute("DELETE FROM user WHERE id = {0}".format(getid))
            db.session.commit()
            i+=1
    GMT = pytz.timezone('Singapore')
    now = datetime.now(GMT)
    datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
    new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Multiple Delete in User Management rows affected " + str(i))
    db.session.add(new_audit)
    db.session.commit()
    flash('Successfully Deleted!')
    return redirect(url_for('userlist.list'))


ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@userlist.route('/importuser', methods = ['GET', 'POST'])
@login_required
@admin_required
def importuser():
    if request.method == 'POST':
        if 'excelfile' not in request.files:
            flash("No files are selected", category="error")
            return render_template('importuser.html', user=current_user)
        excel = request.files['excelfile']
        if excel.filename == '':
            flash("No Selected File", category="error")
            return render_template("importuser.html" , user=current_user)

        excel.save(os.path.join(current_app.config["UPLOAD_FOLDER"], excel.filename))
        filename_path = os.path.join(current_app.config["UPLOAD_FOLDER"], excel.filename)
        data = pd.read_csv(filename_path)
        data.head()
        userin = []
        outcome = ""

        i = 0
        c = 0
        try:
            for col in data.columns:
                i += 1

            if i == 5:
                for i, row in data.iterrows():
                    flag = 0
                    if "," in str(row[0]) or "nan" in str(row[0]) or "/" in str(row[0]) or ";" in str(row[0]) or ":" in str(row[0]) or "'" in str(row[0]) or '"' in str(row[0]) :
                        flag = 1
                    if "nan" in str(row[4]):
                        row[4] = "No Contact Number"
                    if "nan" in str(row[3]):
                        row[3] = "No Name"
                    if "nan" in str(row[1]):
                        row[1] = "password"
                    if "nan" in str(row[2]):
                        row[2] = "User"
                    if not flag:
                        userin.append(userlists(row[0], row[1],row[2],row[3],row[4]))

                for row in userin:
                    user = User.query.filter_by(email=row.emailp).first()
                    if user:
                        outcome += str(row.emailp) + ", "

                    else:
                        my_data = User(email=str(row.emailp), password=generate_password_hash(str(row.passwordp), method='sha256'), roles=str(row.rolesp), name=str(row.namep), contact=str(row.contactp), status = "Inactive")
                        db.session.add(my_data)
                        c += 1

                flash('Email existed: ' + outcome , category='error')
                GMT = pytz.timezone('Singapore')
                now = datetime.now(GMT)
                datetimeformat = datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
                new_audit = UserAudit(datetime=datetimeformat, email=current_user.id, action="Import Excel in User Management rows affected " + str(c))
                db.session.add(new_audit)
                db.session.commit()
                flash("User Imported Successfully from CSV!")

                return redirect(url_for('userlist.list'))
            else:
                flash("User CSV file need to be 5 columns", category="error")

        except:
            flash("Could not read CSV file please try again", category="error")
            return render_template("importuser.html", user=current_user)

    return render_template("importuser.html" , user = current_user)

@userlist.route("/posts")
@login_required
def AllPost():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("AllPost.html", user=current_user, posts=posts)

@userlist.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        category = request.form.get('category')
        status = request.form.get('status')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id, category=category, status=status)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('userlist.AllPost'))

    return render_template('create_post.html', user=current_user)

@userlist.route("/delete-post,<id>,<author>,<userid>")
@login_required
def delete_post(id, author,userid):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif userid != author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('userlist.AllPost'))


@userlist.route("/posts,<name>")
@login_required
def posts(name):
    user = User.query.filter_by(name=name).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('userlist.posts(name)'))

    posts = user.posts
    status = request.form.get('status')
    return render_template("posts.html", user=current_user, posts=posts, name=name, status=status)

@userlist.route("/categoryposts,<category>")
@login_required
def post(category):
    posts = Post.query.filter_by(category=category).order_by(Post.id.desc()).all()

    return render_template("statuspost.html", user=current_user, posts=posts, category=category)


@userlist.route("/create-comment,<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('userlist.AllPost'))


@userlist.route("/delete-comment,<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('userlist.AllPost'))


@userlist.route("/like-post,<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = LikePost.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = LikePost(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})

#update post status
@userlist.route('/updatepoststatus,<post_id>', methods = ['GET', 'POST'])
def updatepoststatus(post_id):
    if request.method == 'POST':
        post = Post.query.filter_by(id=post_id).first()

        post.status = request.form['status']

        db.session.commit()
        flash("Status Updated Successfully")

        return redirect(url_for('userlist.AllPost'))
