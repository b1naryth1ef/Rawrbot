from flask import Flask, render_template

app = Flask(__name__)

class Obj(object):
    def __init__(self, data={}):
        self.__dict__.update(data)

@app.route('/')
def view_root():
    return render_template('base.html')

if __name__ == "__main__":
    app.run(debug=True)