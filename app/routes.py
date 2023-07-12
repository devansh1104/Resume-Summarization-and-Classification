from flask import Flask, render_template, request, redirect, session, flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from app.forms import RegistrationForm,LoginForm
import os
from app.retext import resumeExtractor
import pandas as pd
from app.test import extract_resume_information
from app.gpt import jd_analysis, category_prediction, generate_summary, lst_jd_analysis, category_matching_percentage
import pandas as pd
import os
from werkzeug.utils import secure_filename
import shutil
from app.models import User
from app import app,db,bcrypt
from flask_login import login_user

import string
import random
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def generate_random_text(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def category_number(resumes):
    category_results2 = []
    for resume in resumes:
        category_result2 = random.randint(1, 100)
        category_results2.append(category_result2)  
    return category_results2



def category_prediction(resumes):
    category_resultss1 = []
    category_resultss2 = []
    category_resultss3 = []
    df = pd.DataFrame()
    for resume in resumes:
        category_result1 = generate_random_text(5) 
        category_result2 = random.randint(1, 100)
        #category_result3 = generate_random_text(20) 
        category_result3 = "Basis of classification: The resume highlights the candidate's skills and experience in software development, including programming languages, frameworks, and tools. The candidate also mentions their education and relevant projects, demonstrating their expertise in this field." 
        category_resultss1.append(category_result1)
        category_resultss2.append(category_result2)
        category_resultss3.append(category_result3)
    df['Category'] = category_resultss1
    df['Matching Percentage'] = category_number(resumes)
    df['Basis of Classification'] = category_resultss3    
    return df
    return summary_df

def generate_summaryy(resume_df):
    det_sum_list=[]
    con_sum_list=[]
    resume_id=[]
    for i in range(len(resume_df)):
        detailed_summary="Big data"
        concise_summary="Small Data"
        resume=resume_df['Resume'][i]
        det_sum_list.append(detailed_summary)
        con_sum_list.append(concise_summary)
        resume_id.append(resume_df["Name"][i])
    summary_df = pd.DataFrame()
    #summary_df["Resume ID"]=resume_id
    summary_df["Summary"]=con_sum_list
    summary_df["Detailed Summary"]= det_sum_list
    print(summary_df)
    return summary_df


@app.route('/',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created!You are now able to log in','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password','danger')
    return render_template('login.html',title='Login',form=form)



@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_description = request.files['job_description']
        job_description_filename = secure_filename(job_description.filename)
        job_description_path = os.path.join(app.config['UPLOAD_FOLDER'], job_description_filename)
        job_description.save(job_description_path)
        fetch_job = resumeExtractor.extractorData(job_description_path, "docx")
        fetch_job = fetch_job[5]
        resume_folder = request.form['resume_folder']
        session['resume_folder'] = resume_folder
        #session['job_description_filename'] = job_description_filename
        #print(job_description_filename)
        result_list = extract_resume_information(resume_folder)
        resumes = result_list['Resume']
        filenames = result_list['File Name']
        #df = category_prediction(resumes)
        print("Hi")
        df = category_matching_percentage(fetch_job, result_list)
        print("Hi")
        #print(df)
        if 'Filename' not in df.columns:
            df.insert(0, 'Filename', filenames)

        print(df)
        for filename in os.listdir(resume_folder):
            source_path = os.path.join(resume_folder, filename)
            destination_path = os.path.join(app.static_folder, filename)
            shutil.copy(source_path, destination_path)

        #filename = os.path.basename(job_description_path)

        return render_template('results.html', df=df, filename=filename)
    return render_template('index.html')


@app.route('/file/<filename>')
def file_page(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template('pdf_viewer.html', filename=filename, file_path=file_path)


@app.route('/summarization', methods=['POST'])
def summarization():
    df=pd.DataFrame()
    session['df'] = df
    selected_files = request.form.getlist('selectedFiles')[:-1] 
    resume_folder = session.get('resume_folder')  
    new_resume_folder = 'selected_resumes'  
    if not os.path.exists(new_resume_folder):
        os.makedirs(new_resume_folder)
    
    for filename in selected_files:
        source_path = os.path.join(resume_folder, filename) 
        destination_path = os.path.join(new_resume_folder, filename)
        shutil.copy(source_path, destination_path)
    
    result_list = extract_resume_information(new_resume_folder) 
    resumes = result_list['Resume']
    filenames = result_list['File Name']
    #df = generate_summaryy(result_list)
    print("Summarisation starts")
    df = generate_summary(result_list)

    print(df)
    if 'Filename' not in df.columns:
        df.insert(0, 'Filename', filenames)

    print(df)
    for filename in os.listdir(new_resume_folder):
        file_path = os.path.join(new_resume_folder, filename)
        os.remove(file_path)

    print("hi")
    print(df)
    print("hi")
    session['df'] = df

    return render_template('summary.html', df=df)


@app.route('/detailed_summary/<filename>')
def detailed_summary(filename):
    df = session.get('df')
    print(df)
    selected_row = df[df['Filename'] == filename]
    detailed_summary = selected_row['Detailed Summary'].iloc[0]
    return render_template('detailed_summary.html', detailed_summary=detailed_summary)
