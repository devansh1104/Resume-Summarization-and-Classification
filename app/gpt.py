import openai
#from test import result,fetch_job
import time
from termcolor import colored
import pandas as pd
import tiktoken
import os
import pickle
from app.retext import resumeExtractor
import pandas as pd

def Total_tokens(message, information_retrieval_model):
    encoding = tiktoken.encoding_for_model(information_retrieval_model)
    return len(encoding.encode(message))
def Group_Chunks_for_Information_Extraction(result, token_limit, information_retrieval_model):
    if(len(result) == 0):
        return []
    grouped_chunks = []
    chunks = ""
    arr = result.split(' ')
    for i in arr:
        if(Total_tokens((chunks+" " + i), information_retrieval_model) <= token_limit):
            chunks+=" " +i
        else:
            grouped_chunks.append(chunks)
            chunks = i
    grouped_chunks.append(chunks)
    return grouped_chunks


# Set up OpenAI API credentials
openai.api_key=''
total_requests_till_now = 0
last_request_time = 0
summary_df=pd.DataFrame()

def Limit_Max_Requests_per_minute():
    global total_requests_till_now
    global last_request_time
    if(total_requests_till_now == 0 or time.time() - last_request_time > 60 + 1):      # 60s = 1 min (+1 for safe side)
        last_request_time = time.time()
        total_requests_till_now = 1
    elif(time.time() - last_request_time <= 60 and total_requests_till_now < 3):   # max no. of requests = 3 per min

        total_requests_till_now += 1
    else:                                                                  # wait for 1 min to be over for next API request.
        time_to_wait = (60+1) - (time.time() - last_request_time)      
        # +1s was done to compromise in some cases where python rounds off 45.2743492493243289 to 45.
        print(colored("Please wait for {} seconds.....".format(time_to_wait), 'red'))

        time.sleep(time_to_wait)

        last_request_time = time.time()

        total_requests_till_now = 1

def gpt_response(chunk,instruction):
    prompt = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": chunk},
        ]
    Limit_Max_Requests_per_minute()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.5
    )  
    response_message = response["choices"][0]["message"]["content"]
    return response_message

def generate_summary(resume_df):
    det_sum_list=[]
    con_sum_list=[]
    resume_id=[]
    for i in range(len(resume_df)):
        detailed_summary=""
        concise_summary=""
        resume=resume_df['Resume'][i]
        res_chunk=Group_Chunks_for_Information_Extraction(resume, 3700, "gpt-3.5-turbo")
        instruction=f"I am going to give you resume data in the form of chunks and give you a total of {len(res_chunk)} number of chunks after this. Analyze them and generate a compiled summary at the end when I tell you to."
        response = gpt_response("", instruction)
        for i in range(len(res_chunk)):
            instruction = f"This is chunk number {i+1}"
            response = gpt_response(res_chunk[i],instruction)
            detailed_summary+=response+" "
        instruction = "Now we have reached the end of the resume, generate a compiled summary now"
        response = gpt_response("", instruction)
        concise_summary+=response
        det_sum_list.append(detailed_summary)
        con_sum_list.append(concise_summary)
        resume_id.append(resume_df["Name"][i])
    #summary_df["Resume ID"]=resume_id
    summary_df["Summary"]=con_sum_list
    summary_df["Detailed Summary"]= det_sum_list
    print(summary_df)
    return summary_df

def category_prediction(resume_df):
    cat_list=[]
    basis_class=[]    
    resume_id=[]
    for i in range(len(resume_df)):
        resume=resume_df['Resume'][i]
        # prompt=f"Resume:\n"+"\n".join(resume)+"Give one most relevant job profile to which the resume belongs to?"
        res_chunk=Group_Chunks_for_Information_Extraction(resume, 100, "gpt-3.5-turbo")
        # print(res_chunk)
        instruction=f"I am going to give you resume data in the form of chunks and give you a total of {len(res_chunk)} number of chunks after this. Predict the category of Job profile that they belong to at the end when I tell you to."
        response = gpt_response("", instruction)
        # print("Instruction supplied:",response)
        for i in range(len(res_chunk)):
            instruction = f"This is chunk number {i+1}"
            response = gpt_response(res_chunk[i],instruction)
        instruction = "Now we have reached the end of the resume, generate one most suitable category of Job profile that the resume belongs to. Please generate only the Job profile in your response and no other text. In the next line generate the basis of your classification"
        response = gpt_response("", instruction)
        l1=response.split("\n")
        cat_list.append(l1[0])
        basis_class.append(l1[-1])
        resume_id.append(resume_df["Name"][i])
    summary_df["Resume ID"]=resume_id   
    summary_df["Category"]=cat_list
    summary_df["Basis of Classification"]=basis_class
    return summary_df

def jd_analysis(fetch_job, resume_df):
    match_percentage=[]  
    resume_id=[]  
    for i in range(len(resume_df)):
        resume=resume_df['Resume'][i]
        res_chunk=Group_Chunks_for_Information_Extraction(resume, 10, "gpt-3.5-turbo")
        instruction=f"I am going to give you resume data in the form of chunks and give you a total of {len(res_chunk)} number of chunks after this. Predict the percentage of similarity between the supplied job description and the resume at the end when I tell you to."
        response = gpt_response("", instruction)
        print("Instruction supplied:",response)
        for i in range(len(res_chunk)):
            instruction = f"This is chunk number {i+1}"
            response = gpt_response(res_chunk[i],instruction)
            print(f"Chunk{i+1}",response) 
        instruction = f"Now we have reached the end of the resume, compute a percentage which represents a percentage of similarity between the supplied job description and the resume above. Please output only the percentage of similarity and no other text."
        response = gpt_response(fetch_job, instruction)
        print("Final Response",response)
        match_percentage.append(response)
        resume_id.append(resume_df["Name"][i])
    summary_df["Resume ID"]=resume_id
    summary_df["Matching Percentage"]=match_percentage
    return summary_df



def lst_jd_analysis(fetch_job, resume_df):
    match_percentage=[]  
    resume_id=[]  
    for i in range(len(resume_df)):
        resume=resume_df['Resume'][i]
        # prompt=f"Resume:\n"+"\n".join(resume)+"Give one most relevant job profile to which the resume belongs to?"
        res_chunk=Group_Chunks_for_Information_Extraction(resume, 3700, "gpt-3.5-turbo")
        # print(res_chunk)
        instruction=f"I am going to give you resume data in the form of chunks and give you a total of {len(res_chunk)} number of chunks after this. Predict the percentage of similarity between the supplied job description and the resume at the end when I tell you to."
        response = gpt_response("", instruction)
        # print("Instruction supplied:",response)
        for i in range(len(res_chunk)):
            # prompt=f"Chunk {i+1}: {res_chunk[i]}"
            instruction = f"This is chunk number {i+1}"
            # Get GPT-3 response
            response = gpt_response(res_chunk[i],instruction)
            # print(f"Chunk{i+1}",response)
        instruction = f"Now we have reached the end of the resume, compute a percentage which represents a percentage of similarity between the supplied job description and the resume above. Please output only the percentage of similarity and no other text."
        response = gpt_response(fetch_job, instruction)
        # print("Final Response",response)
        match_percentage.append(response)
        resume_id.append(resume_df["Name"][i])
    # summary_df["Resume ID"]=resume_id
    # summary_df["Matching Percentage"]=match_percentage
    return match_percentage



def category_matching_percentage(fetch_job,resume_df):
    cat_list=[]
    basis_class=[]    
    #resume_id=[]
    for i in range(len(resume_df)):
        resume=resume_df['Resume'][i]
        # prompt=f"Resume:\n"+"\n".join(resume)+"Give one most relevant job profile to which the resume belongs to?"
        res_chunk=Group_Chunks_for_Information_Extraction(resume, 3700, "gpt-3.5-turbo")
        # print(res_chunk)
        instruction=f"I am going to give you resume data in the form of chunks and give you a total of {len(res_chunk)} number of chunks after this. Predict the category of Job profile that they belong to at the end when I tell you to."
        response = gpt_response("", instruction)
        # print("Instruction supplied:",response)
        for i in range(len(res_chunk)):
            # prompt=f"Chunk {i+1}: {res_chunk[i]}"
            instruction = f"This is chunk number {i+1}"
            # Get GPT-3 response
            response = gpt_response(res_chunk[i],instruction)
            # print(f"Chunk{i+1}",response)
        instruction = "Now we have reached the end of the resume, generate one most suitable category of Job profile that the resume belongs to. Please generate only the Job profile in your response and no other text. In the next line generate the basis of your classification"
        response = gpt_response("", instruction)
        l1=response.split("\n")
        # print("Final Response",response)
        # print(l1)
        cat_list.append(l1[0])
        basis_class.append(l1[-1])
        #resume_id.append(resume_df["Name"][i])

    #summary_df["Resume ID"]=resume_id  
    summary_df["Category"]=cat_list
    summary_df["Matching Percentage"]=lst_jd_analysis(fetch_job,resume_df)
    summary_df["Basis of Classification"]=basis_class
    print(summary_df)

    return summary_df