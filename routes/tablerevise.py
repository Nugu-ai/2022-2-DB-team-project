from flask import Blueprint, render_template


bp = Blueprint('tablerevise', __name__, url_prefix='/tablerevise', template_folder='templates')

@bp.route('/')
def dblogin():
    return render_template("tablerevise.html")