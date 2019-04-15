import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_advertisement_condition():
    with open('advertisement.conf', 'r') as conf_file:
        conditions = [line.split(' ', 1) for line in conf_file.readlines()]

    with open('advertisement_condition.py', 'w') as condition_file:
        condition_file.write('def get_advertisement(total_people, moving_in, moving_out, moving_left, moving_right):\n')
        # print(conditions)
        for cond in conditions:
            condition_file.write('    if {}:\n'.format(cond[1].strip()))
            condition_file.write('        return \'{}\'\n'.format(cond[0]))
        condition_file.write('    return None\n')




def upload(request, upload_folder, condition):
    if request.method == 'POST':
        # check if the post request has the required parts
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        if 'description' not in request.form:
            flash('No description part')
            return redirect(request.url)

        file = request.files['file']
        description = request.form['description']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # condition.acquire()
        # condition.wait()

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))

            with open("advertisement.conf", "a") as f:
                # print(file.filename,description)
                f.write(file.filename + ' ' + description + '\n')

            create_advertisement_condition()

        # condition.notifyall()
        # condition.release()

        return redirect(url_for('upload_advertisement'))

