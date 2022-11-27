from flask import Blueprint, render_template, session, redirect, url_for
import db


bp = Blueprint('tablescan', __name__, url_prefix='/tablescan', template_folder='templates')


# ===================================================
# 대상 테이블 선택
# ===================================================
@bp.route('/', methods=['GET'])
def tablescan():
    if 'database' in session:
        try:
            conn = db.get_db()
            with conn:
                cur = conn.cursor()
                table_list_stmt = 'SELECT `table_name` FROM TABLE_LIST'
                cur.execute(table_list_stmt)
                all_table_list = []
                for table_name in cur.fetchall():
                    attr_list_stmt = f'SELECT `attr_name`, `record_count` FROM `ATTR` WHERE `table_name` = "{table_name[0]}"'
                    cur.execute(attr_list_stmt)
                    attrs = []
                    records = 0
                    for attr_name, record_count in cur.fetchall():
                        attrs.append(attr_name)
                        records = record_count
                    all_table_list.append({"table_name": table_name[0], "attrs": attrs, "records": records})
            return render_template(
                    'tablescan.html',
                    host=session['host'],
                    port=session['port'],
                    database=session['database'],
                    result=all_table_list)

        except db.DBConnectionError:
            return render_template(
                    'tablescan.html',
                    host=session['host'],
                    port=session['port'],
                    database=session['database'])
    else:
        return redirect(url_for('dblogin.dblogin'))


# ===================================================
# 테이블 속성 도메인 스캔
# ===================================================
@bp.route('/<table_name>')
def scan_table(table_name):
    return table_name