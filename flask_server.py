from flask import session, Flask, render_template,request,redirect,url_for,jsonify,Response
from secret_key import secret_key
from flask_caching import Cache
import re
from process_db import * 
from markupsafe import escape


app = Flask(__name__)

app.config.update(
    SECRET_KEY = secret_key,
    SESSION_COOKIE_SECURE = True,
    PERMANENT_SESSION_LIFETIME = 3600
)

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# # app.config['cached_data'] = None  # Initialize the cached data variable to None
# @cache.cached(timeout=1)  # Cache for 24 hours 86400
# def cached_dk_comps2():
#     return get_dk_comps()

# @cache.cached(timeout=1)  # Cache for 24 hours
# def cached_kommuner2():
#     return get_kommuner()

@app.route('/')
def startPage():
    return render_template('index.html')

@app.route('/submit',methods=['POST'])
def submit():
    # Retrieve the form data
    wcaid = escape(request.form['WCAID']).strip()
    pattern = r'^\d{4}[a-zA-Z]{4}\d{2}$'

    if re.match(pattern, wcaid):
        return redirect(f'/person/{wcaid.upper()}')
    else:
        return "Invalid WCAID format"

@app.route('/person/<wcaid>')
def person_comps(wcaid):
    pattern = r'^\d{4}[a-zA-Z]{4}\d{2}$'
    if re.match(pattern, wcaid):
        # app.config['cached_data'] = None
        # cache.delete('cached_dk_comps')
        # cache.delete('cached_kommuner')
        map_= get_person_kommuner(wcaid.upper(),get_dk_comps(),get_kommuner())._repr_html_()
        # map_= get_person_kommuner(wcaid.upper(),cached_dk_comps2(),cached_kommuner2())._repr_html_()

        return render_template("show_person.html",map_=map_,wcaid=wcaid.upper())
    else:
        return "Invalid WCAID format"

@app.route('/all')
def all_comps():

    map_= get_dk_kommuner(get_dk_comps(),get_kommuner())._repr_html_()
    return render_template("show_person.html",map_=map_)

@app.route('/danmarkskort')
def danmarkskort():

    map_= show_dk_no_comps(get_kommuner())._repr_html_()
    return render_template("show_person.html",map_=map_)

if __name__ == '__main__':
    app.run(port=5000,debug=True)