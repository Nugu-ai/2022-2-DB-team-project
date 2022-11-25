from flask import Blueprint, render_template, request, session, redirect, url_for
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
    2) DB 연결 O: 
        - CSV 업로드 창으로 redirect ('/dblogin/upload')
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
                return redirect(url_for('dblogin.upload'))
            except db.DBConnectionError:
                return render_template("dblogin.html", err='DB 정보 오류')
        else:
            return render_template("dblogin.html")
    else:
        return redirect(url_for('dblogin.upload'))


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
            df = pd.read_csv(file)
            
            # TABLE 생성
            stmt = ''
            for col in df.columns:
                if df[col].dtype == int:
                    stmt += f'`{col}` INT, '
                elif df[col].dtype == float:
                    stmt += f'`{col}` DOUBLE, '
                else:
                    stmt += f'`{col}` VARCHAR(100), '
            create_stmt = f'CREATE TABLE IF NOT EXISTS `{file.filename.split(".")[0]}` ({stmt[:-2]})'
            
            conn = db.get_db()
            with conn:
                cur = conn.cursor()
                cur.execute(create_stmt)

                # Insert row by row
                for idx in df.index:
                    stmt = ''
                    for col in df.columns:
                        if df[col].dtype == object:
                            stmt += f"'{df[col][idx]}', "
                        else:
                            stmt += f"{df[col][idx]}, "
                    insert_stmt = f'INSERT INTO `{file.filename.split(".")[0]}` VALUES ({stmt[:-2]})'
                    print(insert_stmt)
                    cur.execute(insert_stmt)

                conn.commit()

            return render_template(
                'upload.html',
                host=session['host'],
                port=session['port'],
                database=session['database'],
                msg=f'{file.filename} 업로드 성공')
        else:
            return render_template(
                'upload.html',
                host=session['host'],
                port=session['port'],
                database=session['database'])
    else:
        return redirect(url_for('dblogin.dblogin'))
