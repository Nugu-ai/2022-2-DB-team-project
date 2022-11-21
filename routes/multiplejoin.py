from flask import Blueprint, render_template


bp = Blueprint('multiplejoin', __name__, url_prefix='/multiplejoin', template_folder='templates')

@bp.route('/')
def multiplejoin():
    return render_template("multiplejoin.html")