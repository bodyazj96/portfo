import os
import csv
import glob
import shutil
from fpdf import FPDF
from PIL import Image, ImageFilter, ImageOps
from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
from werkzeug.utils import secure_filename
from flask_recaptcha import ReCaptcha

UPLOAD_FOLDER = './uploaded_files'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = "APP_SECRET_KEY"
app.config['RECAPTCHA_SITE_KEY'] = 'SITE_KEY'
app.config['RECAPTCHA_SECRET_KEY'] = 'SECRET_KEY'
recaptcha = ReCaptcha(app=app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

user_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'new_folder')

@app.route('/pdf_with_images/<name>')
def preview_pdf_with_images(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)

@app.route('/imgtopdf', methods=['GET', 'POST'])
def insert_images_to_pdf():
	
"""
This function inserts images to a pdf it creates. One page - one image

"""

    if request.method == 'POST':
        
	# verifying reCAPTCHA:
	
        if recaptcha.verify():
            message = 'Thanks for filling out the form!'
        else:
            message = 'Please fill out the ReCaptcha!'
            flash(message, 'error')
            return render_template('imgtopdf.html')

        # removing a pdf file created by a previous user from upload folder:
	
        for file in glob.glob(f"{app.config['UPLOAD_FOLDER']}/*.*"):
            os.remove(file)
        
	"""
	uploading user's images; creating directory for user's files (if does not exist);
	checking if user's files have allowed extensions; uploading files to user_dir:
	
	"""
	
        files = request.files.getlist('files[]')
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(user_dir, filename))
        
	"""
	adjusting images' resolution for better efficiency; sharpening the images;
        using EXIF code to position images correctly on page (according to their native orientation):
	"""
	
        for item in glob.glob(f"{user_dir}/*.*"):
            img = Image.open(item)
            img.thumbnail((800, 820))
            i = img.filter(ImageFilter.SHARPEN)
            im = ImageOps.exif_transpose(i)
            im.save(item)
	
	"""
	inserting adjusted images to a pdf page by page;
        user chooses image's position on page and the name of the pdf file which will be created: 
	"""
        
        pdf = FPDF()
        imagelist=[]
        pdftitle = request.form['pdf_name']

        for file in glob.glob(f'{user_dir}/*.*'):
            imagelist.append(file)
        for image in imagelist:
            pdf.add_page()
            option = request.form['position']
            if option == 'center':
                pdf.image(image, x=50, y=80, w=110)
            elif option == 'top right corner':
                pdf.image(image, x=100, y=0, w=110)
            elif option == 'top left corner':
                pdf.image(image, x=0, y=0, w=110)
            elif option == 'bottom right corner':
                pdf.image(image, x=100, y=150, w=110)
            elif option == 'bottom left corner':
                pdf.image(image, x=0, y=150, w=110)
        pdf.output(f"{app.config['UPLOAD_FOLDER']}/{pdftitle}.pdf", "F")
	
	# removing user_dir containing user's images:
	
        shutil.rmtree(user_dir)
	
	# redirecting user to the page containing PDF viewer; user can view their pdf file with images there:
	
        return redirect(url_for('preview_pdf_with_images', name=f'{pdftitle}.pdf'))

@app.route("/")
def my_home():
    return render_template('index.html')

@app.route("/<string:page_name>")
def html_page(page_name):
	return render_template(f'{page_name}')

def write_to_csv(data):
	with open('database.csv', newline='', mode='a') as database:

		email=data['email']
		subject=data['subject']
		message=data['message']

		csv_writer=csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		csv_writer.writerow([email,subject,message])

@app.route('/contact', methods=['POST', 'GET'])

def contact_me():

    if request.method == 'POST':

        if recaptcha.verify():
            message = 'Thanks for filling out the form!'
        else:
            message = 'Please fill out the ReCaptcha!'
            flash(message, 'error')
            return render_template('contact.html')

        try:
            data = request.form.to_dict()
            write_to_csv(data)
            return redirect('/thank_you.html')
        except:
            return "Did not save to database"
    else:
        return "Something went wrong. Try again."
