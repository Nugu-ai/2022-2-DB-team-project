from flask import Blueprint, render_template


bp = Blueprint('dblogin', __name__, url_prefix='/dblogin', template_folder='templates')

@bp.route('/')
def dblogin():
    return render_template("dblogin.html")