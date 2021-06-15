import os
import csv
import glob
from fpdf import FPDF
from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:/Users/bodya/Desktop/web server/uploaded_files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = "2f7507b6ba103d240d9d7535dac60ea697be7ee2"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/imgtopdf', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'files[]' not in request.files:
			flash('No file part')
			return redirect(request.url)
		files = request.files.getlist('files[]')
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		# if files.filename == '':
		# 	flash('No selected file')
		# 	return redirect(request.url)
		for file in files:
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		pdf = FPDF()
		imagelist=[]
		for file in glob.glob('C:/Users/bodya/Desktop/web server/uploaded_files/*.png'):
			imagelist.append(file)
		for image in imagelist:
			pdf.add_page()
			pdf.image(image, w=190, h=150)
		pdf.output("C:/Users/bodya/Desktop/web server/uploaded_files/your_file.pdf", "F")
		return redirect(url_for('download_file', name='your_file.pdf'))

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
