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
        d = dict()
        subject_id = request.form['subject_id']

        # TODO rest of the model here.
        d['user_id'] = subject_id

        pictures = database.get_relevant_pictures_for_user(subject_id)

        if not pictures:
            return render_template('no_pictures_for_user.html', id=subject_id)

        d['picture_name'] = pictures[0]
        eval_data = database.get_evaluation_data_for_picture(
                d['picture_name'])

        d['focused_people'] = eval_data[2]
        d['unfocused_people'] = eval_data[3]

        return render_template('survey.html', data=d)

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
