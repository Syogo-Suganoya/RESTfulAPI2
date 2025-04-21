from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return jsonify(message="Hello from Flask on Render!")


# デバッグモードで動かさないよう注意
if __name__ == "__main__":
    app.run()
