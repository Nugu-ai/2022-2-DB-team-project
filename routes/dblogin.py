from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
import pymysql
import pandas as pd
import db


bp = Blueprint('dblogin', __name__, url_prefix='/dblogin', template_folder='templates')

# ===================================================
# DB 접속
# ===================================================
@bp.route('/', methods=['GET', 'POST'])
def dblogin():
    """
    1) DB 연결 X:
        - GET: dblogin.html 표시
        - POST: 입력된 정보로 DB 접속 시도, 성공 시 session에 DB 정보 저장
    """
    if 'database' not in session:
        if request.method == 'POST':
            DB = {}
            for key in request.form:
                DB[key] = request.form[key]
            DB['port'] = int(DB['port'])
            try:
                conn = pymysql.connect(**DB)
                conn.close()
                for key in DB:
                    session[key] = DB[key]
                return render_template(
                        'dblogin.html',
                        host=session['host'],
                        port=session['port'],
                        database=session['database'],
                        user=session['user'],
                        msg='DB 연결 성공')
            except pymysql.Error:
                return render_template("dblogin.html", msg='DB 연결 실패')
        else:
            return render_template("dblogin.html")
    else:
        return render_template(
                'dblogin.html',
                host=session['host'],
                port=session['port'],
                database=session['database'],
                user=session['user'])


# ===================================================
# CSV 파일 업로드
# ===================================================
@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    1) DB 연결 X: 
        - DB 연결 창으로 redirect ('/dblogin')
    2) DB 연결 O: 
        - GET: upload.html 표시
        - POST: 첨부된 csv 파일을 읽고 DB에 테이블 생성
        
    * DB 연결은 db.py의 get_db() 사용
    """
    if 'database' in session:
        if request.method == 'POST':
            file = request.files['csv']
            df = pd.read_csv(file, encoding='cp949') # 한글 입력시 오류 생겨서 encoding 처리했습니다.
            
            conn = db.get_db()
            with conn:
                cur = conn.cursor()

                # CSV -> TABLE 생성
                table_name = file.filename.split(".")[0]
                all_table_list_stmt = f'SELECT `table_name` FROM `TABLE_LIST`'
                cur.execute(all_table_list_stmt)
                all_table_list = []
                for names in cur.fetchall():
                    all_table_list.append(names[0])

                if table_name not in all_table_list:
                    col_stmt = ''
                    for col in df.columns:
                        if df[col].dtype == int:
                            col_stmt += f'`{col}` INT, '
                        elif df[col].dtype == float:
                            col_stmt += f'`{col}` DOUBLE, '
                        else:
                            col_stmt += f'`{col}` VARCHAR(100), '
                    create_stmt = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({col_stmt[:-2]})'
                    cur.execute(create_stmt)

                    for idx in df.index:
                        stmt = ''
                        for col in df.columns:
                            if df[col].dtype == object:
                                stmt += f"'{df[col][idx]}', "
                            else:
                                stmt += f"{df[col][idx]}, "
                        insert_stmt = f'INSERT INTO {table_name} VALUES ({stmt[:-2]})'
                        cur.execute(insert_stmt)

                    # TABLE_LIST, ATTR 테이블에 추가
                    table_list_stmt = f'INSERT INTO `TABLE_LIST` VALUES ("{table_name}", "F")'
                    count_stmt = f'SELECT COUNT(*) FROM {table_name}'
                    cur.execute(count_stmt)
                    record_count = cur.fetchone()[0]
                    attr_stmt = 'INSERT INTO `ATTR`(table_name, attr_name, data_type, record_count) VALUES '
                    for col in df.columns:
                        if df[col].dtype == int:
                            attr_stmt += f'("{table_name}", "{col}", "INT", {record_count}), '
                        elif df[col].dtype == float:
                            attr_stmt += f'("{table_name}", "{col}", "DOUBLE", {record_count}), '
                        else:
                            attr_stmt += f'("{table_name}", "{col}", "VARCHAR", {record_count}), '
                    cur.execute(table_list_stmt)
                    cur.execute(attr_stmt[:-2])

                    conn.commit()
                    msg = f'{table_name} 테이블 생성 성공'

                else:
                    msg = f'동일한 이름의 테이블이 존재합니다: {table_name}'

            return render_template(
                'upload.html',
                host=session['host'],
                port=session['port'],
                database=session['database'],
                msg=msg)
        else:
            return render_template(
                'upload.html',
                host=session['host'],
                port=session['port'],
                database=session['database'])
    else:
        return redirect(url_for('dblogin.dblogin'))


# ===================================================
# DB 연결 해제
# ===================================================
@bp.route('/disconnect', methods=['POST'])
def disconnect():
    """
    session에 저장된 DB 정보를 삭제
    """
    if 'database' in session:
        session.pop('host', None)
        session.pop('port', None)
        session.pop('database', None)
        session.pop('user', None)
        session.pop('password', None)

    return redirect(url_for('dblogin.dblogin'))
