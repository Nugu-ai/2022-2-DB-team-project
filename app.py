from flask import Flask, render_template


app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY = 'dev',
)

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


if __name__ == '__main__':
    app.run(debug=True)