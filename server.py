import os
import csv
import glob
import shutil
from fpdf import FPDF
from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploaded_files'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = "2f7507b6ba103d240d9d7535dac60ea697be7ee2"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

user_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'new_folder')

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)

@app.route('/imgtopdf', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
		# check if the post request has the file part
        for file in glob.glob(f"{app.config['UPLOAD_FOLDER']}/*.*"):
            os.remove(file)
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files[]')
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		# if files.filename == '':
		# 	flash('No selected file')
		# 	return redirect(request.url)
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(user_dir, filename))
        pdf = FPDF()
        imagelist=[]
        pdfnamae = request.form['pdf_name']
        for file in glob.glob(f'{user_dir}/*.*'):
            imagelist.append(file)
        for image in imagelist:
            pdf.add_page()
            option = request.form['position']
            if option == 'center':
                pdf.image(image, x=50, y=75, w=110, h=150)
            elif option == 'top right corner':
                pdf.image(image, x=100, y=0, w=110, h=150)
            elif option == 'top left corner':
                pdf.image(image, x=0, y=0, w=110, h=150)
            elif option == 'bottom right corner':
                pdf.image(image, x=100, y=150, w=110, h=150)
            elif option == 'bottom left corner':
                pdf.image(image, x=0, y=150, w=110, h=150)
        pdf.output(f"{app.config['UPLOAD_FOLDER']}/{pdfnamae}.pdf", "F")
        shutil.rmtree(user_dir)
        return redirect(url_for('download_file', name=f'{pdfnamae}.pdf'))

@app.route("/")
def my_home():
    return render_template('index.html')

@app.route("/<string:page_name>")
def html_page(page_name):
	return render_template(f'{page_name}')

# @app.route("/file_ready", methods=['GET', 'POST'])
# def imgtopdf():
#     if request.method == 'POST':
#         f = request.files['file']
#         f.save()
#         return redirect('download_file.html')

def write_to_csv(data):
	with open('database.csv', newline='', mode='a') as database:

		email=data['email']
		subject=data['subject']
		message=data['message']

		csv_writer=csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		csv_writer.writerow([email,subject,message])

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
	if request.method == 'POST':
		try:
			data = request.form.to_dict()
			write_to_csv(data)
			return redirect('/thank_you.html')
		except:
			return "Did not save to database"
	else:
		return "Something went wrong. Try again."
