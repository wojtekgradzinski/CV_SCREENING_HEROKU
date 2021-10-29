from flask import Flask, redirect, url_for, render_template, request
import PyPDF2
import spacy
from spacy.matcher import PhraseMatcher

# import skill extractor
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB
nlp = spacy.load("en_core_web_sm")
# init skill extractor
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

application = Flask(__name__)

@application.route("/", methods=["POST", "GET"])
def home():
  

    scores = {}
    s = 0
  

    def pdf_to_string(pdfReader):
            string_cv = '' 
            for i in range(pdfReader.numPages):

                
                pageObj = pdfReader.getPage(i)
                string_cv = string_cv + ' ' + pageObj.extractText()
            return string_cv
    def skills(annotations):
            skill = []
            for key,_ in annotations['results'].items():
                for ls in annotations['results'][key]:
                    skill.append(ls['skill_id'])
            return skill
    def scoring(job_skills,cv_skills):
        score = 0
        for s in cv_skills:
            if (s in job_skills):
                score +=1
        return score
    
    def display(Scores,s):
        p = {}
        if len(scores) != 0:
            sort_orders = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                
            for i in sort_orders:
                #p = p + str(i[0] + '           fulfills ' + str(round((i[1]/len(s))*100,2)) + '% ' + 'of the required skills \n')
                percentage = round((i[1]/len(s))*100,2)
                p[i[0]] = str(percentage) + '%     ' + status(percentage)

        return p
    def status(x):
        
        if x<=25:
            return 'Poor'
        elif 25<x<=50:
            return 'Medium'
        elif 50<x<=65:
            return 'Good'
        elif 65<x<=90:
            return 'Very good'
        elif x>90:
            return 'Very good'
    if request.method == "POST":

        # cv1 = request.files["file1"]
        # cv2 = request.files["file2"]
        # cv3 = request.files["file3"]

        CVs = request.files.getlist("file")

        job_description = request.form["job"]
        if len(job_description) < 50:
            return render_template("index.html", resume ="Please input the job desciption",dic={})
            #return render_template("index.html", resume =CVs[0].filename)
        

        # if (len(cv1.filename) == 0 and len(cv2.filename) == 0 and len(cv3.filename) == 0):
        #     return render_template("index.html", resume = "Please upload at least one resume")
        

        if (CVs[0].filename == ''):
            return render_template("index.html", resume = "Please upload at least one resume", dic={})

        a = skill_extractor.annotate(job_description)
        s = skills(a)

        for cv in CVs:
        #if (len(cv1.filename) != 0):
            # creating a pdf reader object
            pdfReader1 = PyPDF2.PdfFileReader(cv)
            string_cv1 = pdf_to_string(pdfReader1)
            a1 = skill_extractor.annotate(string_cv1)
            sk1 = skills(a1)
            s1 = scoring(s,sk1)
            scores[cv.filename] = s1


 

     
    return render_template("index.html", resume = '', dic=display(scores,s))



if __name__ == "__main__":
    application.run(debug=True)