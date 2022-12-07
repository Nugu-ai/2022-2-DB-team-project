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
    conn = db.get_db()
    with conn:
        cur = conn.cursor()

        cur.execute('SELECT record_count FROM attr WHERE table_name = %s', [tabledname])
        total_record = cur.fetchall()[0][0]

        # 대표속성
        reprattr = []

        cur.execute('SELECT repr_attr_name FROM repr_attr, std_repr_attr WHERE repr_attr.repr_attr_id = std_repr_attr.repr_attr_id AND table_name = %s', [tabledname])
        for repr_attr_name in cur.fetchall():
            reprattr.append(repr_attr_name)

        # 대표결합키
        joinkey = []

        cur.execute('SELECT key_name FROM join_key, std_join_key WHERE join_key.join_key_id = std_join_key.key_id AND table_name = %s', [tabledname])
        for key_name in cur.fetchall():
            joinkey.append(key_name)

        fin_reprattr = ''
        fin_joinkey = ''

        if len(reprattr) == 0:
            fin_reprattr = '-'
        else:
            reprattr = set(reprattr)
            if len(list(reprattr)) == 1:
                for i in range(0, len(list(reprattr))):
                    fin_reprattr = fin_reprattr + str(list(reprattr)[i][0])    
            else:
                for i in range(0, len(list(reprattr)) - 1):
                    fin_reprattr = fin_reprattr + str(list(reprattr)[i][0]) + ', '
                fin_reprattr += str(list(reprattr)[len(list(reprattr))][0])

        if len(joinkey) == 0:
            fin_joinkey = '-'
        else:
            joinkey = set(joinkey)
            if len(list(joinkey)) == 1:
                for i in range(0, len(list(joinkey))):
                    fin_joinkey = fin_joinkey + str(list(joinkey)[i][0])
            else:
                for i in range(0, len(list(joinkey)) - 1):
                    fin_joinkey = fin_joinkey + str(list(joinkey)[i][0]) + ', '
                fin_joinkey += str(list(joinkey)[len(list(joinkey)) - 1][0])
    
    return render_template(
        'singlejoin_target.html',
        table_name = tabledname,
        total_record = total_record,
        repr_attr = fin_reprattr,
        join_key = fin_joinkey
    )

