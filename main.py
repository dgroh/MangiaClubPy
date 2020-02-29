from flask import Flask

app = Flask(__name__)

app.config.from_pyfile(f"config/{app.config['ENV']}.cfg")

if __name__ == '__main__':
    app.run()