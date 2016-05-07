from flask import *

import csv_reading
import database

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './csv/'


@app.route('/')
def index():
    pics_left = database.count_unevaluated_pictures()

    d = dict()
    d["is_evaluation_complete"] = True if pics_left == 0 else False
    d["pictures_left"] = pics_left
    d['user_ids'] = database.get_waiting_user_ids()
    return render_template('index.html', data=d)


@app.route('/survey/', methods=['POST', 'GET'])
def survey():
    if request.method == 'GET':
        return redirect(url_for('index'))

    f = request.form
    d = dict()
    user_id = f['subject_id']

    # telltale if the dispatch is from the instructions or from a survey page.
    if 'q2' in f:
        database.save_focal_survey_result(f)

    try:
        picture = database.get_next_relevant_picture_for_user(user_id)
    except IndexError:
        return render_template('no_pictures_for_user.html',
                               id=user_id)

    fp, ufp = database.get_evaluation_data_for_picture(picture)

    evals_left = database.get_evaluations_left(picture)

    d['evals_left'] = evals_left
    d['focused_people'] = fp
    d['unfocused_people'] = ufp
    d['subject_id'] = user_id
    d['picture_name'] = picture

    if needs_survey_instructions(fp, evals_left):
        return render_template('instructions.html', d=d)

    if needs_survey(fp, evals_left):
        return render_template('survey.html', d=d)

    if needs_nf_survey(ufp):
        return render_template('nonfocal_instructions.html', d=d)

    if needs_another_survey(user_id):
        return redirect(url_for('survey_recurse', id=user_id))


def needs_survey_instructions(focused_people, iterations_left):
    """Looks whether or not any given picture needs to have survey instructions
    displayed.

    Criteria:
    - No evaluations have been done
    - there are focal subjects to survey the participant about."""

    return (focused_people > 0) and (focused_people == iterations_left)


def needs_survey(focused_people, iterations_left):
    """
     Criteria for another survey being needed:
      - More focused people than done evaluations
      - There are focused people at all.

    :return: Whether or not the given criteria warrant another survey iteration.
    """

    return focused_people > iterations_left > 0


def needs_nf_survey(unfocused_people):
    """
    Criteria for the NF survey being needed:
    - There are unfocused people
    :return:
    """

    return unfocused_people > 0


def needs_another_survey(user_id):
    """
    Returns whether or not the survey should recurse, IE, whether or not the
    participant has any pictures left that have been:
    - evaluated
    - not yet surveyed about
    - showing people.

    :param user_id: The user in question.
    :return: Whether or not another survey is needed.
    """

    next = database.get_next_relevant_picture_for_user(user_id)

    # the query above does not tell me whether or not the survey is already done
    # for that picture. Find out.

    # I should add a 'finished' column in `pictures` and update that in the
    # NF data capture.



@app.route('/survey_recurse/<id>/', methods=['GET'])
def survey_recurse(id):
    next_picture = database.get_next_relevant_picture_for_user(id)

    if not next_picture:
        return redirect(url_for('index'))

    return render_template('recurse.html', id=id)


@app.route('/evaluation/<id>/', methods=['GET', 'POST'])
def eval_userid_pictures(id):
    if request.method == 'GET':
        d = dict()
        d['user_id'] = id

        try:
            d['picture_name'] = database.get_next_user_id_picture(id)[0][0]
        except IndexError:
            return redirect(url_for('index'))

        d['exclusive'] = True

        return render_template('eval.html', data=d)

    if request.method == 'POST':
        database.insert_picture_data(request.form)

        return redirect(url_for('eval_userid_pictures', id=id))


@app.route('/evaluation/', methods=['GET', 'POST'])
def initialise_pictures():
    if request.method == 'GET':
        d = dict()
        try:
            d['picture_name'], d['user_id'] = database.get_next_picture()
        except IndexError:
            return redirect(url_for('index'))

        return render_template('eval.html', data=d)

    if request.method == 'POST':
        database.insert_picture_data(request.form)
        return redirect(url_for('initialise_pictures'))


@app.route('/upload/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'GET':
        return render_template('upload.html')

    if request.method == 'POST':
        database.upload_csv(request.files, app.config['UPLOAD_FOLDER'])
        return redirect(url_for('index'))


@app.route('/dump/', methods=['POST'])
def dump():
    return render_template('dump.html', d=request.form)


@app.route('/drop/db/', methods=['GET'])
def drop_database():
    database.drop_database()
    return redirect(url_for('upload_csv'))


if __name__ == '__main__':
    # app.run(debug=True, port=80, host='0.0.0.0')
    app.run(debug=True)
