import os
from flask import Flask, request, flash, url_for, redirect, \
    render_template, abort, send_from_directory, abort
from werkzeug import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from filters import get_matrix, apply_kernel, produce_output
from ImageFile import ImageFile
from thinning import zs_thin
from features import feature_histogram, trim, zoning_method
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

ALLOWED_EXTENSIONS = set(['bmp'])

app = Flask(__name__)
run_config = 'dev'
app.config.from_pyfile('flaskapp.cfg')
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'img')
app.config['MAX_CONTENT_LENGTH'] = 0.5 * 1024 * 1024
basedir = os.path.abspath(os.path.dirname(__file__))
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/image/<filename>')
def image(filename):
    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return render_template('index.html', filename=filename)
    else:
        return abort(404)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                filename = ImageFile.time_stamp() + secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.close()
                return redirect(url_for('image', filename=filename))
            except RequestEntityTooLarge as e:
                flash('data too large')
                return redirect(url_for('upload'))
        else:
            flash('File extension not allowed. Only .bmp files are supported')
            return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/load', methods=['POST'])
def load():
    filename = "2016-03-03-15-22-00-fruits.bmp"
    if request.form['load'] == "1bit":
        filename = "2015-12-09-01-04-57-test.bmp"
    return redirect(url_for('image', filename=filename))



def convert(n):
    try:
        float(n)
        return float(n)
    except ValueError as v:
        return False


def parse(k):
    if '/' in k:
        fraction = k.split("/")
        numer = convert(fraction[0])
        denom = convert(fraction[1])
        if numer and denom:
            return numer / denom
        else:
            return False
    else:
        n = convert(k)
        return n


def move_file(new_file):
    os.rename(new_file, os.path.join(app.config['UPLOAD_FOLDER'], new_file))
    return


@app.route('/filter', methods=['POST'])
def filter():
    kernel = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    counter = 0
    filename = request.form['filename']

    for k in range(len(kernel)):
        for j in range(len(kernel)):
            n = parse(request.form['k' + str(counter)])
            if n is not False:
                kernel[k][j] = n
                counter += 1
            else:
                flash("Bad kernel value")
                return render_template('index.html', filename=filename)

    img = ImageFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    output = produce_output(kernel, img)
    new_file = img.save_img(output, filename)
    move_file(new_file)
    return render_template('index.html', filename=filename, new_file=new_file)


@app.route('/thinning', methods=['POST'])
def thinning():
    filename = request.form['filename']
    img = ImageFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if img.mode == "1":
        output = zs_thin(img)
        new_file = img.save_img(output, filename, thinning=True)
        move_file(new_file)
        return render_template('index.html', filename=filename, new_file=new_file)
    else:
        flash("Image must have bit depth of 1")
        return redirect(url_for('image', filename=filename))

@app.route('/histogram', methods=['POST'])
def histogram():
    filename = request.form['filename']
    img = ImageFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if img.mode == "1":
        trimmed = trim(img)
        img_vector = feature_histogram(trimmed)
        return render_template('index.html', filename=filename, img_vector=img_vector)
    else:
        flash("Image must have bit depth of 1")
        return redirect(url_for('image', filename=filename))


@app.route('/zoning', methods=['POST'])
def zoning():
    filename = request.form['filename']
    img = ImageFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if img.mode == "1":
        trimmed = trim(img)
        img_vector = feature_histogram(trimmed)
        return render_template('index.html', filename=filename, img_vector=img_vector)
    else:
        flash("Image must have bit depth of 1")
        return redirect(url_for('image', filename=filename))



def compare(method_file, img_vector):
    f = open(method_file)
    minimum = 0
    index = 0

    for j, line in enumerate(f):
        c = 0
        data = line.strip().split(",")
        for i, d in enumerate(data):
            c += (float(d) - img_vector[i])**2  

        if j == 0:
            minimum = c
            number = str(index)
        else:
            if c < minimum:
                minimum = c
                index = j/25
                number = str(index)

    f.close()
    return number


@app.route('/recognize/histogram', methods=['POST'])
def recognize_hist():
    filename = request.form['filename']
    img = ImageFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if img.mode == "1":
        trimmed = trim(img)
        img_vector = feature_histogram(trimmed)
        number = compare("histogram.txt", img_vector)
        return render_template('index.html', filename=filename, number=number, returned=True)
    else:
        flash("Image must have bit depth of 1")
        return redirect(url_for('image', filename=filename))       

@app.route('/recognize/zoning', methods=['POST'])
def recognize_zone():
    filename = request.form['filename']
    img = ImageFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if img.mode == "1":
        trimmed = trim(img)
        img_vector = feature_histogram(trimmed)
        number = compare("histogram.txt", img_vector)
        return render_template('index.html', filename=filename, number=number, returned=True)
    else:
        flash("Image must have bit depth of 1")
        return redirect(url_for('image', filename=filename)) 

if __name__ == '__main__':
    manager.run()
