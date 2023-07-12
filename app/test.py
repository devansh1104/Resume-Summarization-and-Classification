from flask import Flask, render_template, request
import os
from app.retext import resumeExtractor
import pandas as pd
'''
def extract_resume_information(job_path, resume_folder):
    extractorObj = resumeExtractor
    result_list = []
    file_list = os.listdir(resume_folder)
    for filename in file_list:
        file_path = os.path.join(resume_folder, filename)
        fetchedData = extractorObj.extractorData(file_path, filename.rsplit('.', 1)[1].lower())
        result = fetchedData[5]
        res_id = fetchedData[0]
        res_phone = fetchedData[1]

    df = pd.DataFrame()
    df['Name'] = [res_id]
    df['Mobile Number'] = [res_phone]
    df['Resume'] = [result]
    result_list.append(df)

    return result_list
'''

def extract_resume_information(resume_folder):
    extractorObj = resumeExtractor
    result_dict = {}
    file_list = os.listdir(resume_folder)
    
    for filename in file_list:
        file_path = os.path.join(resume_folder, filename)
        fetchedData = extractorObj.extractorData(file_path, filename.rsplit('.', 1)[1].lower())
        result = fetchedData[5]
        res_id = fetchedData[0]
        res_phone = fetchedData[1]
        result_dict[filename] = [res_id, res_phone, result]
    df = pd.DataFrame(result_dict, index=["Name", "Mobile Number", "Resume"]).T
    df.reset_index(inplace=True)  # Adds a new column with row names as values
    df.rename(columns={"index": "File Name"}, inplace=True)  # Renames the column
    return df