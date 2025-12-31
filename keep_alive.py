from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.get("/healthz")
def health():
    return "OK", 200

def run_server():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def run():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()