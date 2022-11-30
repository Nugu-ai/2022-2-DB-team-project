from flask import Blueprint, render_template, session, redirect, url_for, request
import db


bp = Blueprint('tablescan', __name__, url_prefix='/tablescan',
               template_folder='templates')


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
                    all_table_list.append(
                        {"table_name": table_name[0], "attrs": attrs, "records": records})
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
@bp.route('/<table_name>', methods=['GET', 'POST'])
def scan_table(table_name):
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
        'tablescanresult.html',
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
