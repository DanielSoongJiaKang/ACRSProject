from flask import Blueprint, render_template, flash, redirect, url_for
from .models import UserAudit, User
from flask_login import login_required, current_user
from functools import wraps



useraudit = Blueprint('useraudit', __name__)

def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.roles != "Admin":
                flash("You don't have permission to access this resource.", "warning")
                return redirect(url_for("views.home"))
            return func(*args, **kwargs)
        return decorated_view

@useraudit.route('/useraudit')
@login_required
@admin_required
def UserAuditList():
    all_data = UserAudit.query.join(User, UserAudit.email == User.id)
    return render_template("useraudit.html", audit=all_data, user=current_user)