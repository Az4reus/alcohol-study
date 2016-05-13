import time

import sys
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

    if 'q2' in f:
        database.save_focal_survey_result(f)
    if 'nfDone' in f:
        database.save_nf_survey_result(f, ufp)
    if ufp == 0 and evals_left == 0:
        database.set_done(picture)

    if needs_survey_instructions(fp, evals_left, f):
        return survey_instructions()

    if needs_survey(evals_left, f):
        return render_template('survey.html', d=d)

    if needs_nf_instructions(picture, ufp, f):
        return render_template('nonfocal_instructions.html', d=d)

    if needs_nf_survey(f):
        return render_template('nonfocal_survey.html', d=d)

    if needs_another_survey(user_id):
        return redirect(url_for('survey_recurse', id=user_id))

    return redirect(url_for('index'))


@app.route('/survey/dispatch/', methods=['POST'])
def survey_dispatch():
    user_id = request.form['subject_id']
    try:
        picture_id = database.get_next_relevant_picture_for_user(user_id)
    except IndexError:
        print(
                "### ERROR ### - "
                "No relevant pictures for user_id {}, "
                "must be a bug in the selector@index".format(user_id))
        return redirect(url_for('index'))

    focused_people = database.get_picture_eval_data_by_id(picture_id)[3]

    if focused_people > 0:
        return redirect(url_for('survey_instructions', picture_id=picture_id))
    else:
        return redirect(url_for('nf_dispatch', picture_id=picture_id))


@app.route('/instructions/<picture_id>/')
def survey_instructions(picture_id):
    d = dict()
    d['picture_id'] = picture_id

    picture_data = database.get_picture_by_id(picture_id)
    d['picture_name'] = picture_data[1]
    d['focused_people'] = database.get_picture_eval_data_by_id(picture_id)[3]

    return render_template('instructions.html', d=d)


@app.route('/survey/<picture_id>/<iteration>/', methods=['POST', 'GET'])
def survey_page(picture_id, iteration):
    """
    This function renders a survey page for the given picture_id and the given
    iteration. It gathers all the data, and renders it as needed. If posted to,
    data is saved, the iteration is increased, then redirection to the GET
    endpoint.

    :param picture_id: The picture. This is the ROWID of the pictures table.
    :param iteration: The Iteration. This needs to be smaller than the amount
    of focused people, on hitting that amount, a redirect to `nf_dispatch`
    happens.

    :return: Renders a survey page for the specified parameters.
    """
    if request.method == 'POST':
        database.save_focal_survey_result(request.form, iteration)

        try:
            i = int(iteration)
            i += 1
            i = str(i)
        except ValueError:
            i = 1

        return redirect(url_for('survey_page',
                                picture_id=picture_id,
                                iteration=i))

    if request.method == 'GET':
        d = dict()
        d['id'] = picture_id
        d['iteration'] = iteration

        picture_data = database.get_picture_by_id(picture_id)
        d['picture_name'] = picture_data[1]
        d['subject_id'] = picture_data[3]

        eval_data = database.get_picture_eval_data_by_id(picture_id)
        d['focused_people'] = eval_data[3]
        d['unfocused_people'] = eval_data[4]

        if int(iteration) > eval_data[3]:
            return redirect(url_for('nf_dispatch', picture_id=picture_id))
        else:
            return render_template('survey.html', d=d)


@app.route('/nf/<picture_id>/')
def nf_dispatch(picture_id):
    unfocused = database.get_picture_eval_data_by_id(picture_id)[4]

    if unfocused == '':
        unfocused = 0

    if unfocused > 0:
        return redirect(url_for('nf_instructions', picture_id=picture_id))
    else:
        return redirect(url_for('finished', picture_id=picture_id))


@app.route('/nf/instructions/<picture_id>/', methods=['GET'])
def nf_instructions(picture_id):
    d = dict()

    d['picture_name'] = database.get_picture_by_id(picture_id)[1]
    d['unfocused_people'] = database.get_picture_eval_data_by_id(picture_id)[4]
    d['id'] = picture_id

    return render_template('nonfocal_instructions.html', d=d)


@app.route('/nf/survey/<picture_id>/', methods=['GET'])
def nf_survey_page(picture_id):
    if request.method == 'GET':
        d = dict()
        d['id'] = picture_id

        picture_data = database.get_picture_by_id(picture_id)
        d['user_id'] = picture_data[3]
        d['picture_name'] = picture_data[1]
        d['unfocused_people'] = database.get_picture_eval_data_by_id(picture_id)[4]

        return render_template('nonfocal_survey.html', d=d)


@app.route('/finished/<picture_id>/', methods=['GET', 'POST'])
def finished(picture_id):
    if request.method == 'POST':
        ufp = database.get_picture_eval_data_by_id(picture_id)[4]
        database.save_nf_survey_result(request.form, ufp)

        user_id = database.get_user_for_picture_id(picture_id)
        if needs_another_survey(user_id):
            return redirect(url_for('survey_recurse', id=user_id))
        else:
            return redirect(url_for('index'))

    if request.method == 'GET':
        database.set_done(picture_id)

        user_id = database.get_user_for_picture_id(picture_id)
        if needs_another_survey(user_id):
            return redirect(url_for('survey_recurse', id=user_id))
        else:
            return redirect(url_for('index'))


def needs_survey_instructions(focused_people, iterations_left, form):
    """Looks whether or not any given picture needs to have survey instructions
    displayed.

    Criteria:
    - No evaluations have been done
    - there are focal subjects to survey the participant about."""

    return (focused_people > 0) \
           and (focused_people == iterations_left) \
           and ('f_instructions' not in form)


def needs_survey(iterations_left, form):
    """
     Criteria for another survey being needed:
      - More focused people than done evaluations
      - There are focused people at all.

    :return: Whether or not the given criteria warrant another survey iteration.
    """

    return (iterations_left > 0) and ('f_instructions' in form)


def needs_nf_survey(form):
    """
    Criteria for the NF survey being needed:
    - The instructions page has been displayed beforehand.
    :return:
    """

    return 'nfSurvey' in form


def needs_nf_instructions(picture, unfocused_people, form):
    """
    Checks whether or not the described picture needs a NF instructions page.

    Criteria:
    - The survey has not already taken place.
    - There are some unfocused people in the picture.
    """
    return ('nfSurvey' not in form) \
           and unfocused_people > 0 \
           and 'nfDone' not in form


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
    try:
        database.get_next_relevant_picture_for_user(user_id)
    except IndexError:
        return False

    return True


@app.route('/survey_recurse/<id>/', methods=['GET'])
def survey_recurse(id):
    return render_template('recurse.html', id=id)


@app.route('/evaluation/<id>/', methods=['GET', 'POST'])
def eval_userid_pictures(id):
    if request.method == 'GET':
        d = dict()
        d['user_id'] = id

        try:
            d['picture_name'], d['picture_id'] = \
                database.get_next_user_id_picture(id)[0]
        except IndexError:
            return redirect(url_for('index'))

        d['exclusive'] = True

        return render_template('eval.html', data=d)

    if request.method == 'POST':
        database.insert_picture_eval_data(request.form)

        return redirect(url_for('eval_userid_pictures', id=id))


@app.route('/evaluation/', methods=['GET', 'POST'])
def initialise_pictures():
    if request.method == 'GET':
        d = dict()
        try:
            d['picture_name'], d['user_id'], d[
                'picture_id'] = database.get_next_picture()
        except IndexError:
            return redirect(url_for('index'))

        return render_template('eval.html', data=d)

    if request.method == 'POST':
        database.insert_picture_eval_data(request.form)
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
    # app.run(debug=False, port=80, host='0.0.0.0')
    app.run(debug=True)