import os
import pickle
from resext import resumeExtractor
import pandas as pd

fetch_job=resumeExtractor.extractorData((r"C:\Workspace\Projects\Resume Summarizer\ResumeRanker_Shared\env\ResumeRanker_Shared\Implementation\job_desc.docx"),"docx")


def main():
    # print("hi")
    
    extractorObj = resumeExtractor
    path = r"c:\Workspace\Projects\Resume Summarizer\Resume-Summarization-and-Classification\Sample Resume Folders"

    # for filename in os.listdir(path):
    #     fetchedData=extractorObj.extractorData(path+"\\"+filename,filename.rsplit('.',1)[1].lower())
    #     print(fetchedData)
    result=[]
    file_list = os.listdir(path)

    for i in range(len(file_list)):
      fetchedData=extractorObj.extractorData(path+"\\"+file_list[i],file_list[i].rsplit('.',1)[1].lower())
      result.append(fetchedData[5])
      
    df=pd.DataFrame()
    df['Resume']= result

    return df
result=main()
print(result)
