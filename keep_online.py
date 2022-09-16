# This shall be used whenever the runs out.

from threading import Thread
from flask import Flask
from flask import render_template
import codecs

app = Flask(
    "app", 
    template_folder="templates", # name of folder containing html templates
    static_folder="static" # name of folder for static files
)
@app.route("/")
def home():
  return render_template("cool.html")

def run():
  app.run(host='0.0.0.0', port=3000)

t = Thread(target = run)
t.start()