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


@app.route('/instructions/<picture_id>/')
def survey_instructions(picture_id):
    d = dict()
    d['picture_id'] = picture_id()

    picture_data = database.get_picture_by_id(picture_id)
    d['picture_name'] = picture_data[1]

    fp, _ = database.get_evaluation_data_for_picture(picture_data[3])
    d['focused_people'] = fp

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
        database.save_focal_survey_result(request.form)
        return redirect(url_for('survey_page',
                                picture_id=picture_id,
                                iteration=(iteration + 1)))

    if request.method == 'GET':
        d = dict()
        d['id'] = picture_id
        d['iteration'] = iteration

        picture_data = database.get_picture_by_id(picture_id)
        d['picture_name'] = picture_data[1]
        d['subject_id'] = picture_data[3]

        fp, ufp = database.get_evaluation_data_for_picture(picture_data[1])
        d['focused_people'] = fp
        d['unfocused_people'] = ufp

        if iteration == fp:
            return redirect(url_for('nf_dispatch', id=id))

        return render_template('survey.html', d=d)


@app.route('/nf/dispatch/<picture_id>/')
def nf_dispatch(picture_id):
    pass


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
    # app.run(debug=True, port=80, host='0.0.0.0')
    app.run(debug=True)
