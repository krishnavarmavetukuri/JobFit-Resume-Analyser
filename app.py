from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
import google.generativeai as genai
import fitz 
import os
import markdown2


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)


def gemini_text_response(jobDesc_text, pdf_content, button_prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([jobDesc_text, pdf_content, button_prompt])
    return response.text

def text_from_pdf(uploaded_file):
    if uploaded_file:
        pdf_content = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
            for page in pdf:
                pdf_content += page.get_text()
        return pdf_content
    else:
        raise FileNotFoundError("No file uploaded")



button_prompts_to_gemini = {
    "1": """
        As a skilled reviewer of resumes, your task is to provide a thorough evaluation of the submitted resume. 
Assess the candidate's qualifications, experiences, and accomplishments in relation to the job they are applying for. 
Offer constructive feedback on the overall presentation, layout, and content of the resume. 
Highlight strengths and suggest improvements to enhance its effectiveness in securing job opportunities.i am taking this info from gemini pro and displaying in webpage and the format keeps on changing can you make the headings in bold and i should not get *heading* like this as output and make sure the points are alligned, and if there is a subheading with some related text with ':' make sure they are like this 'subheading:text',do not mention about formating in the output
print in the above asked format itself dont print the same text from the document please use your intelligence to find out and give the review in the asked manner.(Assess the candidate's qualifications, experiences, and accomplishments in relation to the job they are applying for. 
Offer constructive feedback on the overall presentation, layout, and content of the resume. )
format is (Feedback on the overall presentation in points , Feedback on the  layout in points , and Feedback on the content of the resume in points , Strengths, Suggestions for improvement )
    """,
    "2": """
    Your task is to first what you have to say is by seeing his resume how much package per annum can he ask the interviewer when asked and next provide guidance on negotiating a competitive salary package in the current job market landscape.  
Drawing on your knowledge of the current job market trends and requirements, evaluate the resume's suitability for present-day job opportunities. Assess the alignment of the candidate's profile with the skills, experiences, and qualifications sought after by employers in today's competitive landscape.Offer insights into how the candidate can tailor their resume to better position themselves for success in the current job market environment.i am taking this info from gemini pro and displaying in webpage and the format keeps on changing can you make the headings in bold and i should not get *heading* like this as output and make sure the points are alligned, and if there is a subheading with some related text with ':' make sure they are like this 'subheading:text',do not mention about formating in the output
format is (Suitable Salary Range in Indian Rupees, Guidance for Negotiating a Competitive Salary Package, Resume Suitability for Current Job Market)
            
    """,
    "3": """
Your task is to calculate and provide a match score indicating how well the candidate's resume aligns with the given job description. 
Utilize your expertise to analyze the document and assess the degree of fit based on key criteria such as skills, experiences, and qualifications. 
Deliver a clear and quantitative evaluation of the resume's compatibility with the requirements outlined in the job description.
After all the above is displayed then give the missing keywords list which are missing in the resume that are to be there actually when checked from job description.
i am taking this info from gemini pro and displaying in webpage and the format keeps on changing can you make the headings in bold and i should not get *heading* like this as output and make sure the points are alligned, and if there is a subheading with some related text with ':' make sure they are like this 'subheading:text',do not mention about formating in the output
format is (percentage match, missing keywords, Skills and Qualifications(after understanding the resume))
            
    """,
    "4": """
Your expertise is needed to identify any gaps in the candidate's professional skillset as reflected in their resume. 
Carefully review the document to pinpoint any essential skills or qualifications that are missing or inadequately represented. 
Provide recommendations on the types of skills or experiences the candidate should consider acquiring or highlighting to strengthen their candidacy in the job market.
So basically You have to display me the Missing Skills in the candidate's professional skillset in his resume that are required for the job and Reccommend them how to develop those skills.
i am taking this info from gemini pro and displaying in webpage and the format keeps on changing can you make the headings in bold and i should not get *heading* like this as output and make sure the points are alligned, and if there is a subheading with some related text with ':' make sure they are like this 'subheading:text',do not mention about formating in the output
format is (gaps in professional Skillset, Recommendations for acquiring the gaps Skills )
    """
}


@app.route('/')
def index():
    return render_template('main.html')

@app.route('/response_formatting', methods=['POST'])
def response_formatting():
    jobDesc_text = request.form['jobDesc']
    uploaded_file = request.files['file']
    pdf_content = text_from_pdf(uploaded_file)
    prompt_key = request.form['prompt']
    button_prompt = button_prompts_to_gemini[prompt_key]
    response = gemini_text_response(jobDesc_text, pdf_content, button_prompt)
    text = markdown2.markdown(response)

    return jsonify({"response": text})


if __name__ == '__main__':
    app.run(debug=True)