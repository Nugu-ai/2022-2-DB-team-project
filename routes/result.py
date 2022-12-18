from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import pymysql
import db


bp = Blueprint('result', __name__, url_prefix='/result', template_folder='templates')


"""
계속해서 쓰이는 변수들 설명
    result_root : 결과조회 페이지들의 URL 맨 앞에 항상 붙는 부분
    type : 제공할 서비스 종류. 
           html파일에서 if문을 통해 어떤 페이지를 보여줄지 구분하기 위한 용도 
"""

#처음 기본화면
@bp.route('/')
def select():
    global result_root 
    result_root = url_for('result.select')
    
    return render_template("result.html",result_root = result_root)


#스캔 결과조회 화면
@bp.route("/scan/")
def scan_select():
    global result_root 
    
    conn = db.get_db()
    cursor = conn.cursor()
    
    #스캔된 테이블들만 고르는 SQL문
    select_table_sql = """
        SELECT table_name
        FROM TABLE_LIST
        WHERE is_scanned = 'T'
    """
    
    cursor.execute(select_table_sql)
    tables = cursor.fetchall()
    
    
    return render_template("result.html",result_root = result_root,
                           type = 'scan_select', 
                           table_rows = tables)

#어떤 테이블을 선택했을 때, 그 테이블의 스캔결과를 보여주는 화면
@bp.route("/scan/<table_name>/")
def scan_result(table_name):
    global result_root
    
    conn = db.get_db()
    cursor = conn.cursor()
    
    #수치속성들을 불러오는 SQL문
    numerical_row_sql = """
        SELECT ATTR.attr_name, data_type, record_count, distinct_count, null_count, null_count/record_count,  zero_count, zero_count/record_count,  min_value, max_value
        From ATTR, NUMERIC_ATTR
        WHERE ATTR.table_name = NUMERIC_ATTR.table_name
        AND ATTR.attr_name = NUMERIC_ATTR.attr_name
        AND ATTR.table_name = '{0}'
    """.format(table_name)
    
    #범주속성들을 불러오는 SQL문
    categorical_row_sql = """
        SELECT ATTR.attr_name, data_type, record_count, distinct_count, null_count,  null_count/record_count,  symbol_count
        From ATTR, CATEGORICAL_ATTR
        WHERE ATTR.table_name = CATEGORICAL_ATTR.table_name 
        AND ATTR.attr_name = CATEGORICAL_ATTR.attr_name
        AND ATTR.table_name = '{0}'
    """.format(table_name)
    
    cursor.execute(numerical_row_sql)
    numerical_rows = cursor.fetchall()
    
    cursor.execute(categorical_row_sql)
    categorical_rows = cursor.fetchall()
    
    return render_template("result.html", result_root = result_root,
                           type = 'scan_result',
                           table_name = table_name,
                           numeric_rows = numerical_rows,
                           categoric_rows = categorical_rows)

#결합 결과들의 리스트를 보여주는 SQL문
#사용자가 선택한 조건들을 주소의 일부분으로 포함
@bp.route("/JOINlist/<type>/<used_table>/<join_ratio_limit>/<min_record_num_limit>/")
def single_select(type,used_table, join_ratio_limit, min_record_num_limit):
    global result_root
    
    conn = db.get_db()
    cursor = conn.cursor()
    
    #기본 sql문
    joined_result_sql = """
    SELECT * 
    FROM {0}_JOIN_TABLE_LIST
    WHERE id IS NOT NULL
    """.format(type)
    
    #사용자로부터 조건을 입력받지 않으면, NONE으로 조건에 대응되는 주소부분 값 설정
    #조건을 입력받을경우, 조건값에 대응되는 주소부분 값으로 설정(html 상에서)
    #주소를통해 조건이 있음을 인식 >> 그에 해당하는 SQL 조건문 추가
    if used_table != "NONE" :
        joined_result_sql += " AND (source_table_name = '{0}' OR target_table_name = '{0}')".format(used_table)
    
    if join_ratio_limit != "NONE" :
        joined_result_sql += " AND (source_success_rate >= '{0}' OR target_success_rate >= '{0}')".format(join_ratio_limit)
    
    if min_record_num_limit != "NONE" :
        joined_result_sql += " AND joined_record_count >= '{0}'".format(min_record_num_limit)
    
    cursor.execute(joined_result_sql)
    joined_result = cursor.fetchall()
    
    return render_template("result.html",
                           type = type,
                           result_root = result_root,
                           joined_result = joined_result)

@bp.route("/JOINresult/<type>/<table_A>/<table_B>")
def join_result(type, table_A, table_B) :
    
    global result_root
    
    conn = db.get_db()
    cursor = conn.cursor()
    
    return render_template("result.html",
                           type = 'result',
                           result_root = result_root)