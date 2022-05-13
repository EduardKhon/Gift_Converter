from typing import Union
import os
import io

import docx2txt
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, send_file
from werkzeug.utils import secure_filename

def convert_to_gift(filename: str, text: str) -> (bool, str):
    text_clean = [i for i in text.split("\n") if len(i) > 0]
    numeric = []
    unnumeric = []
    n = 0
    for i in text_clean:
        if '№' in i:
            numeric.append(i)
            n = 0
        elif 'Manba' in i:
            numeric.append(i)
        elif 'Qiyinlik darajasi' in i:
            numeric.append(i)
        elif "?" in i:
            unnumeric.append('::'+i)
            unnumeric.append('::'+i)
            numeric.append('::'+i)
            numeric.append('::'+i)
        else:
            if n < 4:
                if n == 0:
                    unnumeric.append('='+i)
                    numeric.append('='+i)
                else:
                    unnumeric.append('~'+i)
                    numeric.append('~'+i)
                n += 1
    full_text = ''
    for i in unnumeric:
        full_text += i+'\n'
    with open(f"{filename}.gift", "w", encoding="utf-8") as file:
        file.write(full_text)
    for i in numeric:
        print(i)
    for i in unnumeric:
        print(i)
    return True, ""


def convert_to_aiken(filename: str, text: str) -> (bool, str):
    text_clean = [i for i in text.split("\n") if len(i) > 0]
    numeric = []
    unnumeric = []
    n = 0
    variant = {
        '0': 'A',
        '1': 'B',
        '2': 'C',
        '3': 'D'
    }
    for i in text_clean:
        if '№' in i:
            numeric.append(i)
            n = 0
        elif 'Manba' in i:
            numeric.append(i)
        elif 'Qiyinlik darajasi' in i:
            numeric.append(i)
        elif "?" in i:
            unnumeric.append(i)
            numeric.append(i)
        else:
            if n < 4:
                unnumeric.append(f'\t{variant[str(n)]}) {i}')
                numeric.append(f'\t{variant[str(n)]}) {i}')
                if n == 3:
                    unnumeric.append('ANSWER: A')
                    numeric.append('ANSWER: A')
                n += 1
    full_text = ''
    for i in unnumeric:
        full_text += i+'\n'
    with open(f"{filename}.aiken", "w", encoding="utf-8") as file:
        file.write(full_text)
    for i in numeric:
        print(i)
    for i in unnumeric:
        print(i)
    return True, ""


def convert_to_txt(file: Union[str, list], single=False, multi=False, request="gift") -> (bool, str):
    """
    file: [str | list]
    `
    single=True, multi=False
    single=False, multi=True
    `
    request: [str] gift | aiken
    """
    convert = {
        "gift": convert_to_gift,
        "aiken": convert_to_aiken
    }
    if single:
        text = docx2txt.process(file)
        status = convert[request](''.join(file.split(".")[0].split('/')[-1]), text)
        if status[0] is True:
            pass
        else:
            return False, "This {file} call ERROR!"
    elif multi:
        for el in file:
            try:
                text = docx2txt.process(el)
                status = convert[request](file.split(".")[0:-1], text)
                if status[0] is True:
                    pass
                else:
                    return "Error! {el} call some ERROR {status[1]}"
            except Exception:
                return False, f"`{el}` is not readable format"
UPLOAD_FOLDER = "uploads\\"
ALLOWED_EXTENSIONS = {'docx'}
app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 512*1024*1024


def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            convert_to_txt(os.path.join(app.config['UPLOAD_FOLDER'], filename), single=True, request="gift")
            print("saved file successfully")
            return redirect('/downloadfile/'+ ''.join(filename.split(".")[0:-1])+".gift")
    return render_template("index.html")


@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)

@app.route('/return-files/<filename>')
def return_files(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')

def run_server() -> None:
    app.run(debug=True, host='0.0.0.0', port=8000)



if __name__ == "__main__":
    run_server()
