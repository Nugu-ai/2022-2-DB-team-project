import db
from flask import Blueprint, redirect, render_template, request, session, url_for
import pandas as pd
from pandas.api.types import is_numeric_dtype


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
        saveAttr = []
        saveRttr = []

        cur.execute( 
            'SELECT DISTINCT R.attr_name, S.repr_attr_name FROM repr_attr R, attr A, std_repr_attr S WHERE R.repr_attr_id = S.repr_attr_id AND R.attr_name = A.attr_name AND R.table_name = %s', [tabledname])
        for attr_name, repr_attr_name in cur.fetchall():
            saveAttr.append(attr_name)
            saveRttr.append(repr_attr_name)
        
        for at in attr:
            check = False
            for num in range(len(saveAttr)):
                if at == saveAttr[num]:
                    check = True
                    break
                else:
                    check = False
                                
            if(check):
                attrname_RA.append(saveAttr[num])
                reprattr.append(saveRttr[num])
            else:
                attrname_RA.append("-")
                reprattr.append("-")
                
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
# 테이블 속성 삭제, 데이터형 변경, 결합키 매핑
# ===================================================
@bp.route('/<table_name>/delete', methods=['GET', 'POST'])
def delete_attr(table_name):
    tabledname = table_name

    conn = db.get_db()
    with conn:
        cur = conn.cursor()
        
        #삭제
        getDeleteList = request.form.getlist('check')

        for name in getDeleteList:
            cur.execute('DELETE FROM attr WHERE attr_name = %s AND table_name = %s' , ([name],[tabledname]))
            conn.commit()

        #데이터형 변경
        attr = []
        datype = []
        isnumeric = []

        cur.execute(
            'SELECT attr_name, data_type, is_numeric FROM attr WHERE table_name = %s', [tabledname]
        )

        for attr_name, data_type, is_numeric in cur.fetchall():
            attr.append(attr_name)
            datype.append(data_type)
            isnumeric.append(is_numeric)
        
        for num in range(len(attr)):
            asdf = request.form.get(attr[num])
            if datype[num] != asdf:
                if isnumeric[num] == 'T':
                    if(asdf in ["INTEGER", "INT", "DOUBLE", "FLOAT"]):
                        if(asdf == "INTEGER"): 
                            cur.execute('UPDATE ATTR SET data_type = "INT", WHERE attr_name = %s AND table_name = %s', (attr[num], tabledname))
                            conn.commit()
                        else:
                            cur.execute('UPDATE ATTR SET data_type = %s, WHERE attr_name = %s AND table_name = %s', (asdf, attr[num], tabledname))
                            conn.commit()
                    elif(asdf in ["VARCHAR", "TEXT", "LONGTEXT"]):
                        cur.execute('DELETE FROM NUMERIC_ATTR WHERE attr_name = %s AND table_name = %s', (attr[num], tabledname))
                        cur.execute('UPDATE ATTR SET data_type = %s, is_numeric = "F" WHERE attr_name = %s AND table_name = %s', (asdf,attr[num], tabledname))
                        cur.execute("INSERT INTO CATEGORICAL_ATTR VALUES (%s, %s, 0)", (tabledname, attr[num]))
                        conn.commit()
                else:
                    
                    if(asdf in ["INTEGER", "INT", "DOUBLE", "FLOAT"]):
                        languageFlag = False
                        cur.execute(f'SELECT {attr[num]} FROM {tabledname}')
                        for project in cur.fetchall():
                            try:
                                number = float(project[0])
                                languageFlag = False
                            except TypeError:
                                languageFlag = True
                            except ValueError:
                                languageFlag = True
                        
                        if languageFlag == False:
                            cur.execute('DELETE FROM CATEGORICAL_ATTR WHERE attr_name = %s AND table_name = %s', (attr[num], tabledname))
                            if asdf == "INTEGER": asdf = "INT"
                            cur.execute('UPDATE ATTR SET data_type = %s, is_numeric = "T" WHERE attr_name = %s AND table_name = %s', (asdf, attr[num], tabledname))

                            cur.execute(
                                f'SELECT COUNT(*) FROM {table_name} WHERE `{attr[num]}` = 0')
                            zero_count = cur.fetchone()[0]

                            cur.execute(
                                f'SELECT MAX(`{attr[num]}`) FROM {table_name}')
                            max_value = cur.fetchone()[0]

                            cur.execute(
                                f'SELECT MIN(`{attr[num]}`) FROM {table_name}')
                            min_value = cur.fetchone()[0]

                            cur.execute("INSERT INTO NUMERIC_ATTR VALUES (%s, %s, %s, %s, %s)", (tabledname, attr[num], zero_count, min_value, max_value))
                            conn.commit()
                    elif(asdf in ["VARCHAR", "TEXT", "LONGTEXT"]):
                        cur.execute('UPDATE ATTR SET data_type = %s WHERE attr_name = %s AND table_name = %s', (asdf,attr[num], tabledname))
                        conn.commit()
        
        #결합키 매핑
        join_key_list = {}
        cur.execute('SELECT `key_id`, `key_name` FROM `STD_JOIN_KEY`')
        for key_id, key_name in cur.fetchall():
            join_key_list[key_name] = key_id

        for key in request.form.keys():
            if request.form[key] == 'Null':
                checklist = []
                attr_name = key[:-3]
                cur.execute(f'SELECT attr_name FROM JOIN_KEY WHERE table_name ="{tabledname}"')
                for att in cur.fetchall():
                    print(att)
                    checklist.append(att[0])
                
                if attr_name not in checklist:
                    continue
                else:
                    cur.execute(f'DELETE FROM JOIN_KEY WHERE attr_name = "{attr_name}" AND table_name = "{tabledname}"')
                    continue
            
            print(key)
            attr_name = key[:-3]

            if key[-2:] == 'JK':
                join_key_name = request.form[key]
                join_key_id = join_key_list[join_key_name]

                checklist = []
                cur.execute(f'SELECT attr_name FROM JOIN_KEY WHERE table_name ="{tabledname}"')
                for att in cur.fetchall():
                    print(att)
                    checklist.append(att[0])

                if attr_name not in checklist: 
                    stmt = f'INSERT INTO `JOIN_KEY` VALUES ("{table_name}", "{attr_name}", {join_key_id})'
                else:
                    stmt = f'UPDATE JOIN_KEY SET JOIN_KEY_ID = "{join_key_id}" WHERE TABLE_NAME = "{table_name}" AND ATTR_NAME = "{attr_name}"'
                cur.execute(stmt)
        
        conn.commit()
 
    return redirect(url_for('tablerevise.tablelist', table_name = tabledname)) 