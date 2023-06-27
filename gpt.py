import openai
from test import result,fetch_job
# Set up OpenAI API credentials
openai.api_key = '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'
# Define function to get GPT-3 response
def get_gpt3_response(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5
    )
    return response.choices[0].text.strip()
#predicting the category of the resume

for i in range(len(result)):
    resume=result['Resume'][i]
    prompt=f"Resume:\n"+"\n".join(resume)+"To which job profile does the resume belong to?"
    
    # Get GPT-3 response
    response = get_gpt3_response(prompt)
    print(response)

#matching job description
lst_percentage=[]
for i in range(len(result)):
    job_description=fetch_job[5]
    resume=result['Resume'][i]
    prompt=f"Job Description: {job_description}\nResumes:\n" + "\n".join(resume) + "\nQuestion: Calculate the percentage of matching between the job description and the supplied resumes"
    response = get_gpt3_response(prompt)
    lst_percentage.append(response)    
    
result['Matching Percentage']=lst_percentage


# # Define the job description and resumes
# job_description = "We are looking for a software engineer with experience in Python and web development."
# resumes = [
#     "I am a software engineer with 5 years of experience in Python and web development.",
#     "As a web developer, I have worked on various Python-based projects.",
#     "I have extensive knowledge in Python programming and web development.",
#     "I am a software engineer specializing in web development using Python and Django.",
# ]

# # Prepare input prompt for GPT-3 model
# prompt = f"Job Description: {job_description}\nResumes:\n" + "\n".join(resumes) + "\nQuestion: Tell the percentage of matching between the job description and the supplied resumes



# # Get GPT-3 response
# response = get_gpt3_response(prompt)

# Print the response

