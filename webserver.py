from flask import Flask, redirect, url_for
app = Flask(__name__)

@app.route("/")
def root():
    return redirect(url_for('static', filename='impulse.html'))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
