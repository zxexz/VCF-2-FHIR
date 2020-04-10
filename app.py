from flask import Flask, render_template, send_file, request
from translator.multithreading import translate
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/translate", methods=['POST'])
def translatevcf():
    filename=request.files['fileToUpload']
    VCF_FILE = '/home/admin1/Documents/projects/py-vcf-2-fhir/HG00628.b37.CYP2C19.vcf'
    try:
        translate(VCF_FILE,"a","m","c",True)
        return send_file('/home/admin1/Documents/projects/py-vcf-2-fhir/pyvcf/downloads/json/fhir.json', attachment_filename='fhir')
    except:
        return send_file('/home/admin1/Documents/projects/py-vcf-2-fhir/pyvcf/downloads/resultEmpty.vcf', attachment_filename='resultEmpty.vcf')

if __name__ == "__main__":
    app.run()
