from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

from routes import dblogin, tablescan, tablerevise, singlejoin, multiplejoin, result

app.register_blueprint(dblogin.bp)
app.register_blueprint(tablescan.bp)
app.register_blueprint(tablerevise.bp)
app.register_blueprint(singlejoin.bp)
app.register_blueprint(multiplejoin.bp)
app.register_blueprint(result.bp)

# @app.route('/dblogin')
# def dblogin():
#     return render_template("dblogin.html")

# @app.route('/tablescan')
# def tablescan():
#     return render_template("tablescan.html")

# @app.route('/tablerevise')
# def tablerevise():
#     return render_template("tablerevise.html")

# @app.route('/singlejoin')
# def singlejoin():
#     return render_template("singlejoin.html")

# @app.route('/multiplejoin')
# def mulriplejoin():
#     return render_template("multiplejoin.html")

# @app.route('/result')
# def result():
#     return render_template("result.html")

if __name__ == '__main__':
    app.run(debug=True)