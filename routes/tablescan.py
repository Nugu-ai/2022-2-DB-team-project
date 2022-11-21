from flask import Blueprint, render_template


bp = Blueprint('tablescan', __name__, url_prefix='/tablescan', template_folder='templates')

@bp.route('/')
def dblogin():
    return render_template("tablescan.html")