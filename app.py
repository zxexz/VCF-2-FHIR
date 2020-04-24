from flask import Flask, render_template, send_file, request
from translator.multithreading import translate
import translator.config as config

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/translate", methods=['POST'])
def translatevcf():
    VCF_FILE=request.files['fileToUpload']
    patientID = VCF_FILE.filename.split('.')[0]
    build = VCF_FILE.filename.split('.')[1]
    geneType = VCF_FILE.filename.split('.')[2]
    if VCF_FILE.filename.split('.')[3] in ["m","M","Male","male"]:
        gender = 'M'
    else:
        gender = 'F'
    try:
        translate(VCF_FILE,patientID,build,geneType.upper(),False,gender)
        return send_file(config.path+'/downloads/json/fhir.json', as_attachment=True,mimetype='application/json',attachment_filename='fhir.json')
    except:
        return send_file(config.path+'/downloads/emptyFHIR.json', as_attachment=True,mimetype='application/json', attachment_filename='emptyFHIR.json')

@app.route("/samples")
def samples():
        return send_file(config.path+'/downloads/vcf.zip', as_attachment=True,mimetype='application/zip',attachment_filename='samples.zip')
    
if __name__ == "__main__":
    app.run()
