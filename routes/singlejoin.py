from flask import Blueprint, render_template


bp = Blueprint('singlejoin', __name__, url_prefix='/singlejoin', template_folder='templates')

@bp.route('/')
def dblogin():
    return render_template("singlejoin.html")