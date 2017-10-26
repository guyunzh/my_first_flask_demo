# -*- coding:utf-8 -*-
from flask import render_template, abort, flash, redirect, url_for, current_app, request,make_response
from . import main
from flask_login import login_required, current_user
from ..models import User, Post,Role, Permission,Comment
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,CommentForm
from .. import db
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        # _get_current_object作用是返回当前对象，current_user只是一个轻度包装的代替者
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed=False
    show_myself=False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
        show_myself = bool(request.cookies.get('show_myself',''))
    if show_followed:
        query=current_user.followed_posts.order_by(Post.timestamp.desc())
    elif show_myself:
        query=current_user.posts.order_by(Post.timestamp.desc())
    else:
        query=Post.query.order_by(Post.timestamp.desc())
    pagination = query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    # posts=Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts, show_followed=show_followed,
                           show_myself=show_myself,pagination=pagination)


@main.route('/user/<username>')  # 用户资料显示页面
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit_profile', methods=['GET', 'POST'])  # 普通用户修改自身资料信息
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])  # admin修改资料的
@login_required
@admin_required
def edit_profile_admin(id):  # 管理员修改页面
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form=CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post',id=post.id,page=-1))
    page=request.args.get('page',1,type=int)
    if page ==-1:
        page=(post.comments.count()-1) / \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] +1
    pagination =post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False )
    comments=pagination.items
    return render_template('post.html',posts=[post],form=form,comments=comments,pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])  # 修改文章的
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')  # 用于关注用户的路由
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('作者不存在.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')  # 取消关注
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid user.")
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not followed this user.')
        return redirect(url_for(".user", username=username))
    current_user.unfollow(user)
    flash('You are now unfollowing %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')  # 分页显示粉丝
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of', endpoint='.followers',
                           pagination=pagination, follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followed by', endpoint='.followed_by',
                           pagination=pagination, follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    resp.set_cookie('show_myself', '')
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    resp.set_cookie('show_myself', '')
    return resp


@main.route('/myself')
@login_required
def show_myself():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '')
    resp.set_cookie('show_myself', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/moderate')            #用来管理评论的显示视图
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False    )
    comments=pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))



# @main.route('/')
# @main.route('/',methods=['GET','POST'])
# def index():
#     form=NameForm()#创建一个表格
#     if form.validate_on_submit():#用户点击提交按钮
#         user=User.query.filter_by(username=form.name.data).first()#从数据库中查找
#         if user is None:
#             user=User(username=form.name.data)
#             db.session.add(user)
#             session['known']=False
#             if current_app.config['FLASKY_ADMIN']:
#                 send_email(current_app.config['FLASKY_ADMIN'],'New User',
#                            'mail/new_user',user=user)
#         else:
#             session['known']=True
#         session['name']=form.name.data
#         return redirect(url_for('.index'))
#     return render_template('index.html',form=form,name=session.get('name'),
#                            known=session.get('known', False))
