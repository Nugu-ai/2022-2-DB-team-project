from flask import Blueprint, render_template


bp = Blueprint('result', __name__, url_prefix='/result', template_folder='templates')

@bp.route('/')
def dblogin():
    return render_template("result.html")