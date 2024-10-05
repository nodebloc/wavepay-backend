from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return {
        "status": True,
        "message": "You probably shouldn't be here, but...",
        "data": {
            "service": "wavepay-api",
            "version": "1.x"
        }
    }

if __name__ == "__main__":
    app.run(debug=True)