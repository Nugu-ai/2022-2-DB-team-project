from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import pymysql
import db


bp = Blueprint('result', __name__, url_prefix='/result', template_folder='templates')



@bp.route('/')
def select():
    global result_root 
    result_root = url_for('result.select')
    
    return render_template("result.html",result_root = result_root)



@bp.route("/scan/")
def scan():
    global result_root
    
    conn = db.get_db()
    cursor = conn.cursor()
    
    numerical_row_sql = """
        SELECT ATTR.table_name, ATTR.attr_name, data_type, record_count, distinct_count, null_count, null_count/record_count,  zero_count, zero_count/record_count,  min_value, max_value
        From ATTR, NUMERIC_ATTR
        WHERE ATTR.table_name = NUMERIC_ATTR.table_name 
        AND ATTR.attr_name = NUMERIC_ATTR.attr_name
    """
    
    categorical_row_sql = """
        SELECT ATTR.table_name, ATTR.attr_name, data_type, record_count, distinct_count, null_count,  null_count/record_count,  symbol_count
        From ATTR, CATEGORICAL_ATTR
        WHERE ATTR.table_name = CATEGORICAL_ATTR.table_name 
        AND ATTR.attr_name = CATEGORICAL_ATTR.attr_name
    """
    
    cursor.execute(numerical_row_sql)
    numerical_rows = cursor.fetchall()
    
    cursor.execute(categorical_row_sql)
    categorical_rows = cursor.fetchall()
    
    return render_template("result.html",result_root = result_root,
                           type = 'scan', 
                           numeric_rows = numerical_rows,
                           categoric_rows = categorical_rows)

@bp.route("/single/")
def single():
    global result_root
        
    return render_template("result.html",
                           type = 'single',
                           result_root = result_root)

@bp.route("/multiple/")
def multiple():
    global result_root
    
    return render_template("result.html",
                           type = 'multiple',
                           result_root = result_root)
