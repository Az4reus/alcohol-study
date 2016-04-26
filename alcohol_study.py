from flask import *
import database

app = Flask(__name__)


@app.route('/')
def index():
    pics_left = database.count_unevaluated_pictures()

    d = dict()
    d["is_evaluation_complete"] = True if pics_left == 0 else False
    d["pictures_left"] = pics_left
    return render_template('index.html', data=d)


@app.route('/survey/', methods=['POST', 'GET'])
def survey():
    if request.method == 'POST':
        return request.form["subject_id"]

    if request.method == 'GET':
        redirect(url_for('index'))


@app.route('/evaluation/', methods=['GET', 'POST'])
def initialise_pictures():
    if request.method == 'GET':
        d = dict()
        d['picture_name'] = database.get_next_picture()

        return render_template('eval.html', data=d)

    if request.method == 'POST':
        database.insert_picture_data(request.form)
        return redirect(url_for('initialise_pictures'))


@app.route('/dropdown/', methods=['GET'])
def dropdown_mockup():
    d = dict()
    d['user_ids'] = database.get_user_ids()

    return render_template('dropdown.html', data=d)

if __name__ == '__main__':
    app.run(debug=True)
