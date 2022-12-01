from flask import Blueprint, render_template, session, redirect, url_for, request
import db

bp = Blueprint('singlejoin', __name__, url_prefix='/singlejoin', template_folder='templates')


# ===================================================
# source 테이블 검색
# ===================================================
@bp.route('/', methods=['GET'])
def source_table_search():
    if 'database' in session:
        return render_template("singlejoin_source.html")
    else:
        return redirect(url_for('dblogin.dblogin'))

# ===================================================
# target 테이블 검색
# ===================================================
@bp.route('/<table_name>', methods=['GET', 'POST'])
def target_table_search(table_name):
    tabledname = table_name

    return render_template("singlejoin_target.html")

