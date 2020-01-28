from webapp import app
from webapp import pkg
import datetime


@app.route("/")
@app.route("/index")
def index():
    # return_string = str(pkg.add_two(50, 50))
    return_string = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    return_string += "<br>" + pkg.return_path()
    return return_string
    # return "Hello, world!"
