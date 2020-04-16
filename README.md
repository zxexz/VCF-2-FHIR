## **VCF to FHIR Converter**

### Introduction

VCF-formatted files are the lingua franca of next-generation sequencing, whereas [HL7 FHIR](https://www.hl7.org/fhir/) is emerging as a standard language for electronic health record interoperability. A growing number of clinical genomics applications are emerging, based on the [HL7 FHIR Genomics standard](http://hl7.org/fhir/uv/genomics-reporting/index.html). Here, we provide an open source utility for converting variants from VCF format into HL7 FHIR Genomics format. A web-based conversion tool leveraging this utility is [HERE](https://vcf-2-fhir.herokuapp.com/). 

Conceptually, the utility takes a VCF as input and outputs a FHIR Genomics report. We currently convert simple variants (SNVs, Indels), along with zygosity and phase relationships, for autosomes, sex chromosomes, and mitochondrial DNA, as illustrated here: 

![image](https://user-images.githubusercontent.com/46577791/79508219-f4d81500-7fed-11ea-9430-d0eea0949df8.png)

### License and Limitations

Software is available for use under an [Apache 2.0 license](https://opensource.org/licenses/Apache-2.0), and is intended solely for experimental use, to help further Genomics-EHR integration exploration. Software is expressly not ready to be used with identifiable patient data or in delivering care to patients. Code issues should be tracked here. Comments and questions can also be directed to info@elimu.io.

### VCF Requirements

- File must conform to VCF Version 4.1 or later.
- Genotype (FORMAT.GT) must be present
- Multi-sample VCFs are allowed, but only the first sample will be converted.
- Filename must be formatted to include certain ordered, dot-delimited parameters.
  - PatientID (required, first): any string without whitespace
  - Build (required, second): one of 'b37' (aka GRCh37, hg19), or ‘b38’ (aka GRCh38, hg38)
  - Gene (required, third): a valid [HGNC gene symbol](https://www.genenames.org/).
  - Sex (optional, fourth): 'M' or 'F' (used in the conversion of chrX and chrY variants)
  - Extra stuff (optional): Anything else, such as local filename, without whitespace
  - Valid filename examples
    - NA120003.b37.CYP2D6.vcf
    - Patient0123.b38.TPMT.M.File012345.vcf
    - Patient0123.b38.TPMT.File012345.vcf
- Submitted VCF files should contain just that slice intended to be converted. While the VCF file may contain variants from multiple chromosomes, or from regions that extend beyond the stated Gene's boundaries, only variants on the same chromosome as the Gene will be converted. 

### Conversion logic

The conversion creates a FHIR Genomics DiagnosticReport that contains a single 'region studied' observation, zero to many 'variant' observations, and zero to many 'sequence phase relationship' observations. The 'region studied' observation includes the NCBI chromosome-level ('NC_') refSeq for the chromosome whose variants were converted. There is one 'variant' observation for each converted VCF row. There is one 'sequence phase relationship' for each pair-wise phase relationship asserted in the VCF file.

The following VCF rows are excluded from conversion: 
- VCF #CHROM is not the one on which the Gene in the filename resides.
- VCF REF is not a simple character string
- VCF ALT is not a simple character string, comma-separated character string, or '.'.. (Rows where ALT is a token (e.g. 'DEL') are excluded).
- VCF FILTER does not equal 'PASS' or '.'.
- VCF INFO.SVTYPE is present. (Structural variants are excluded).
- VCF FORMAT.GT is null ('./.', '.|.', '.', etc).

Variant observations:
- Are reflections of the VCF. No normalization (i.e. conversion into a canonical form) or liftover (i.e. conversion from one build to another) is performed. 
- Use a 1-based coordinate system, so that the variant position in the FHIR Genomics report is the same as VCF POS. 
- Male sex is assumed if not provided (e.g. for determining allelic state of chrX variants)

## Steps to run the converter on you local machine

**Step 1**- Setting up your system
- Download and install XAMPP from the following link: https://www.apachefriends.org/download.html
- Download and install composer from: https://laravel.com/docs/5.4/#server-requirements
-  Download and install java from: https://www.java.com
- Download zip file of the project from the download button of the git repository
- Extract zip in your local machine
- Open the extracted folder (you should see all the files ex: app, bootstrap, config, etc.)
- Open Command Prompt/Terminal in that folder
- Run the following command: 
    - composer install 

This will install the required components for the converter to run.

Now you are all set to convert .vcf files into fhir.json and fhir.xml format.
<br/>  
**Step 2**- Converting .vcf files
- For Linux/Mac: Open Terminal, For Windows open Command Prompt
- Navigate to the 'vcf-2-fhir' folder or open Terminal/Command Prompt in the 'vcf-2-fhir' folder
- Run the following command 
    - for Windows: php artisan serve
    - for Linux: sudo php artisan serve
- Open a web browser and visit "http://localhost:8000", you should see a VCF-TO-FHIR landing page
- Click on "Choose file" button
- Navigate to your desired '.vcf' file in the newly opened file explorer window
- Select the file and click 'open'
- You should be able to see your selected file name beside 'Choose file' button
- Click on "Click To Convert" button
- You will see "fhir.xml has been successfully created" message if your file has been converted successfully
- Click on "VIEW XML FILE" to see fhir.xml file
- If you wish to see fhir.json format:
	-  Open a new Terminal/Command Prompt window
	-  Navigate to the folder "vcf-to-fhir/public" using Terminal/Command Prompt or you can navigate to the folder and then open Terminal/Command Prompt in that folder. Here you should see "xmltojson.jar" file
	- Run the following command "java -jar xmltojson.jar `<local file path where fhir.xml is stored> <filepath where you want to store fhir.json file>`"
	- ex: "java -jar xmltojson.jar Downloads\vcf-to-fhir\public\fhir.xml \Documents\converted"



