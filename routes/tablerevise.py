import db
from flask import Blueprint, redirect, render_template, request, session, url_for


bp = Blueprint('tablerevise', __name__, url_prefix='/tablerevise', template_folder='templates')

# ===================================================
# 대상 테이블 선택
# ===================================================
@bp.route('/', methods=['GET'])
def tablescan():
    if 'database' in session:
        return render_template('tablerevise.html')
    else:
        return redirect(url_for('dblogin.dblogin'))

# ===================================================
# 테이블 속성 스캔 결과
# ===================================================
@bp.route('/<table_name>', methods=['GET', 'POST'])
def tablelist(table_name):
    tabledname = table_name

    conn = db.get_db()
    with conn:
        cur = conn.cursor()

        # 총 레코드 수
        cur.execute(
            'SELECT COUNT(*) FROM attr WHERE table_name = %s', [tabledname])
        total_record = cur.fetchall()[0][0]

        # 속성
        attr = []
        datype = []
        null = []
        record = []
        distinct = []
        candidate = [] 
        isnumeric = []

        cur.execute(
            'SELECT attr_name, data_type, null_count, record_count, distinct_count, is_candidate, is_numeric FROM attr WHERE table_name = %s', [tabledname])
        for attr_name, data_type, null_count, record_count, distinct_count, is_candidate, is_numeric in cur.fetchall():
            attr.append(attr_name)
            datype.append(data_type)
            null.append(null_count)
            record.append(record_count)
            distinct.append(distinct_count)
            candidate.append(is_candidate)
            isnumeric.append(is_numeric)

        # 수치속성
        zero = []
        minv = []
        maxv = []

        cur.execute(
            'SELECT zero_count, min_value, max_value FROM numeric_attr WHERE table_name = %s', [tabledname])
        for zero_count, min_value, max_value in cur.fetchall():
            zero.append(zero_count)
            minv.append(min_value)
            maxv.append(max_value)

        # 범주속성
        symbol = []

        cur.execute(
            'SELECT symbol_count FROM categorical_attr WHERE table_name = %s', [tabledname])
        for symbol_count in cur.fetchall():
            symbol.append(symbol_count[0])

        # 대표속성
        attrname_RA = []
        reprattr = []

        cur.execute(
            'SELECT attr_name, repr_attr_name FROM repr_attr, std_repr_attr WHERE repr_attr.repr_attr_id = std_repr_attr.repr_attr_id AND table_name = %s', [tabledname])
        for attr_name, repr_attr_name in cur.fetchall():
            attrname_RA.append(attr_name)
            reprattr.append(repr_attr_name)

        # 대표결합키
        attrname_JK = []
        joinkey = []

        cur.execute(
            'SELECT attr_name, key_name FROM join_key, std_join_key WHERE join_key.join_key_id = std_join_key.key_id AND table_name = %s', [tabledname])
        for attr_name, key_name in cur.fetchall():
            attrname_JK.append(attr_name)
            joinkey.append(key_name)

        # boxplot
        numeric_attr = ""
        cur.execute(
            'SELECT attr_name FROM attr WHERE is_numeric = "T" AND table_name = %s', [tabledname])
        for attr_name in cur.fetchall():
            numeric_attr += str(attr_name[0]) + ','

        numeric_attr = numeric_attr.rstrip(',')

        cur.execute(f'SELECT {numeric_attr} FROM {tabledname}')
        numeric_attr_data = cur.fetchall()

    return render_template(
        'tablerevise_select.html',
        table_name=tabledname,
        total_record=total_record,
        attr=attr,
        datype=datype,
        null=null,
        record=record,
        distinct=distinct,
        candidate=candidate,
        isnumeric=isnumeric,
        zero=zero,
        minv=minv,
        maxv=maxv,
        symbol=symbol,
        attr_name_RA=attrname_RA,
        attr_name_JK=attrname_JK,
        repr_attr=reprattr,
        join_key=joinkey,
        numeric_attr=numeric_attr,
        numeric_attr_data=numeric_attr_data
    )

# ===================================================
# 테이블 속성 삭제
# ===================================================
@bp.route('/<table_name>/delete', methods=['POST'])
def delete_attr(table_name):
    tabledname = table_name

    conn = db.get_db()
    with conn:
        cur = conn.cursor()

        getDeleteList = request.form.getlist('Ncheck')
        print(getDeleteList)

        for name in getDeleteList:
            cur.execute('DELETE FROM attr WHERE attr_name = %s AND table_name = %s' , ([name],[tabledname]))
            conn.commit()

        # 총 레코드 수
        cur.execute(
            'SELECT COUNT(*) FROM attr WHERE table_name = %s', [tabledname])
        total_record = cur.fetchall()[0][0]

        # 속성
        attr = []
        datype = []
        null = []
        record = []
        distinct = []
        candidate = []
        isnumeric = []

        cur.execute(
            'SELECT attr_name, data_type, null_count, record_count, distinct_count, is_candidate, is_numeric FROM attr WHERE table_name = %s', [tabledname])
        for attr_name, data_type, null_count, record_count, distinct_count, is_candidate, is_numeric in cur.fetchall():
            attr.append(attr_name)
            datype.append(data_type)
            null.append(null_count)
            record.append(record_count)
            distinct.append(distinct_count)
            candidate.append(is_candidate)
            isnumeric.append(is_numeric)

        # 수치속성
        zero = []
        minv = []
        maxv = []

        cur.execute(
            'SELECT zero_count, min_value, max_value FROM numeric_attr WHERE table_name = %s', [tabledname])
        for zero_count, min_value, max_value in cur.fetchall():
            zero.append(zero_count)
            minv.append(min_value)
            maxv.append(max_value)

        # 범주속성
        symbol = []

        cur.execute(
            'SELECT symbol_count FROM categorical_attr WHERE table_name = %s', [tabledname])
        for symbol_count in cur.fetchall():
            symbol.append(symbol_count[0])

        # 대표속성
        attrname_RA = []
        reprattr = []

        cur.execute(
            'SELECT attr_name, repr_attr_name FROM repr_attr, std_repr_attr WHERE repr_attr.repr_attr_id = std_repr_attr.repr_attr_id AND table_name = %s', [tabledname])
        for attr_name, repr_attr_name in cur.fetchall():
            attrname_RA.append(attr_name)
            reprattr.append(repr_attr_name)

        # 대표결합키
        attrname_JK = []
        joinkey = []

        cur.execute(
            'SELECT attr_name, key_name FROM join_key, std_join_key WHERE join_key.join_key_id = std_join_key.key_id AND table_name = %s', [tabledname])
        for attr_name, key_name in cur.fetchall():
            attrname_JK.append(attr_name)
            joinkey.append(key_name)

        # boxplot
        numeric_attr = ""
        cur.execute(
            'SELECT attr_name FROM attr WHERE is_numeric = "T" AND table_name = %s', [tabledname])
        for attr_name in cur.fetchall():
            numeric_attr += str(attr_name[0]) + ','

        numeric_attr = numeric_attr.rstrip(',')

        cur.execute(f'SELECT {numeric_attr} FROM {tabledname}')
        numeric_attr_data = cur.fetchall()

    return render_template(
        'tablerevise_select.html',
        table_name=tabledname,
        total_record=total_record,
        attr=attr,
        datype=datype,
        null=null,
        record=record,
        distinct=distinct,
        candidate=candidate,
        isnumeric=isnumeric,
        zero=zero,
        minv=minv,
        maxv=maxv,
        symbol=symbol,
        attr_name_RA=attrname_RA,
        attr_name_JK=attrname_JK,
        repr_attr=reprattr,
        join_key=joinkey,
        numeric_attr=numeric_attr,
        numeric_attr_data=numeric_attr_data
    )