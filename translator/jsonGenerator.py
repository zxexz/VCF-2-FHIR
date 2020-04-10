import os
import json
import fhirclient.models.diagnosticreport as dr
import fhirclient.models.codeableconcept as concept
import fhirclient.models.meta as meta
import fhirclient.models.resource as resource
import fhirclient.models.observation as observation
import fhirclient.models.fhirreference as reference 
import fhirclient.models.fhirdate as date
import fhirclient.models.range as valRange
import fhirclient.models.medicationstatement as medication
from .allelicstate import getAllelicState
from .phaseswapsort import getSequenceRelation
from collections import OrderedDict
from uuid import uuid4
from .filereader import *
import logging
from .common import *

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M')

def getEmptyFhirJSON(patientID,start,end,refSeq,nocall=False):
    logging.info("[FHIR: Converting XML to JSON]")
    noCallRegion,queryRange = getNoCallableData(NO_CALL_FILE,QUERY_RANGE_FILE)
    nocallRows = len(noCallRegion.index)
    start = queryRange.at[0,"START"]
    end = queryRange.at[0,"END"]

    if not noCallRegion.empty:
        if noCallRegion['START'].iloc[0] <= queryRange['START'].iloc[0]:
            noCallRegion['START'].iloc[0] = queryRange['START'].iloc[0]

        if noCallRegion['END'].iloc[-1] >= queryRange['END'].iloc[0]:
            noCallRegion['END'].iloc[-1] = queryRange['END'].iloc[0]
    else:
        nocall = False

    contained_uid = uuid4().hex[:13]
    patient_reference = reference.FHIRReference({"reference":"Patient/"+patientID})
    variant_reference = reference.FHIRReference({"reference": "#rs-"+contained_uid})

    report = dr.DiagnosticReport()
    report.id = "dr-"+uuid4().hex[:13]
    report.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/diagnosticreport"]})
    report.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"53041-0","display":"DNA region of interest panel"}]})
    report.status = "final"
    report.subject = patient_reference
    report.issued = date.FHIRDate(Utilities.getFhirDate())
    report.result = [variant_reference]

    observation_rs = observation.Observation()
    contained_rs = observation_rs
    observation_dv = observation.Observation()
    contained_dv = observation_dv
    observation_sid = observation.Observation()
    contained_sid = observation_sid
    
    contained_rs.id = "rs-"+contained_uid
    observation_rs.resource_type = "Observation"
    contained_rs.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-region-studied"]})
    observation_rs.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"53041-0","display":"DNA region of interest panel"}]})
    observation_rs.status = "final"
    observation_rs.category = [concept.CodeableConcept({"coding":[{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]})]
    observation_rs.subject = patient_reference
    observation_rs_component1 = observation.ObservationComponent()
    observation_rs_component1.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "51959-5","display": "Range(s) of DNA sequence examined"}]})

    observation_rs_component2 = observation.ObservationComponent()
    observation_rs_component2.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "tbd-coordinate system","display": "Genomic coordinate system"}]})
    observation_rs_component2.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/genetic-coordinate-system","code":"1"}]})

    observation_rs_component3 = observation.ObservationComponent()
    observation_rs_component3.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "48013-7","display": "Genomic reference sequence ID"}]})
    observation_rs_component3.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://www.ncbi.nlm.nih.gov/nuccore","code":refSeq}]})



    if nocall:
        #component Region-studied (No call region)

        nocallComponents = []
        for i in range (nocallRows):
            nocallComponents.append('observation_rs_component'+str(i+4))

        observation_rs_components = []
        for (index, i) in zip(noCallRegion.index, nocallComponents):
            i = observation.ObservationComponent()
            i.code = concept.CodeableConcept({"coding": [{ "system": "http://loinc.org","code": "TBD-noCallRegion","display": "No call region"}]})
            observation_rs_components.append(i)

    if nocall:
        observation_rs.component = [observation_rs_component1,observation_rs_component2,observation_rs_component3] + observation_rs_components
    else:
        observation_rs.component = [observation_rs_component1,observation_rs_component2,observation_rs_component3]

    report.contained = [contained_rs]

    response = report.as_json()
    od = OrderedDict() 
    od["resourceType"] = response['resourceType']
    od["id"] = response['id']
    od["meta"] = response['meta']
    od["contained"] = response['contained']
    od["status"] = response['status']
    od["code"] = response['code']
    od["subject"] = response['subject']
    od["issued"] = response['issued']
    od["result"] = response['result']

    with open(FHIR_JSON_RESULT+'fhir.json', 'w') as fhirJSON:
        fhirJSON.write(json.dumps(od))
    
    return FHIR_JSON_RESULT

# def getFhirJSON(cleanVcf,nextelem,patientID,gender,refSeq,noCall=False):
#     dvuids = {}
#     siduids = []

#     alleles = getAllelicState(cleanVcf,nextelem,gender)
#     sequenceRels = getSequenceRelation(cleanVcf,nextelem)

#     noCallRegion,queryRange = getNoCallableData(NO_CALL_FILE,QUERY_RANGE_FILE)
#     nocallRows = len(noCallRegion.index)
#     start = queryRange.at[0,"START"]
#     end = queryRange.at[0,"END"]

#     if not noCallRegion.empty:
#         if noCallRegion['START'].iloc[0] <= queryRange['START'].iloc[0]:
#             noCallRegion['START'].iloc[0] = queryRange['START'].iloc[0]

#         if noCallRegion['END'].iloc[-1] >= queryRange['END'].iloc[0]:
#             noCallRegion['END'].iloc[-1] = queryRange['END'].iloc[0]
#     else:
#         noCall = False

#     contained_uid = uuid4().hex[:13]
#     patient_reference = reference.FHIRReference({"reference":"Patient/"+patientID})
#     variant_reference = reference.FHIRReference({"reference": "#rs-"+contained_uid})

#     report = dr.DiagnosticReport()
#     report.id = "dr-"+uuid4().hex[:13]
#     report.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/diagnosticreport"]})
#     report.status = "final"
#     report.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"51969-4","display":"Genetic analysis report"}]})
#     report.subject = patient_reference
#     report.issued = date.FHIRDate(Utilities.getFhirDate())

#     observation_rs = observation.Observation()
#     contained_rs = observation_rs
    
#     contained_rs.id = "rs-"+contained_uid
#     observation_rs.resource_type = "Observation"
#     contained_rs.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-region-studied"]})
#     observation_rs.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"53041-0","display":"DNA region of interest panel"}]})
#     observation_rs.status = "final"
#     observation_rs.category = [concept.CodeableConcept({"coding":[{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]})]
#     observation_rs.subject = patient_reference
#     observation_rs_component1 = observation.ObservationComponent()
#     observation_rs_component1.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "51959-5","display": "Range(s) of DNA sequence examined"}]})

#     observation_rs_component2 = observation.ObservationComponent()
#     observation_rs_component2.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "92822-6","display": "Genomic coordinate system"}]})
#     observation_rs_component2.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/genetic-coordinate-system","code":"1"}]})

#     observation_rs_component3 = observation.ObservationComponent()
#     observation_rs_component3.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "48013-7","display": "Genomic reference sequence ID"}]})
#     observation_rs_component3.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://www.ncbi.nlm.nih.gov/nuccore","code":refSeq}]})

#     if noCall:
#         #component Region-studied (No call region)
#         nocallComponents = []
#         for i in range (nocallRows):
#             nocallComponents.append('observation_rs_component'+str(i+4))

#         observation_rs_components = []
#         for (index, i) in zip(noCallRegion.index, nocallComponents):
#             i = observation.ObservationComponent()
#             i.code = concept.CodeableConcept({"coding": [{ "system": "http://loinc.org","code": "TBD-noCallRegion","display": "No call region"}]})
#             observation_rs_components.append(i)
#         observation_rs.component = [observation_rs_component1,observation_rs_component2,observation_rs_component3] + observation_rs_components
#     else:
#         observation_rs.component = [observation_rs_component1,observation_rs_component2,observation_rs_component3]

#     # Observation structure : described-variants
#     obsContained = [contained_rs]
#     for index in alleles.index:
#         dvuid = uuid4().hex[:13]
#         dvuids.update({ str(alleles.at[index,'POS']) : dvuid})

#         observation_dv = observation.Observation()

#         observation_dv = observation.Observation()
#         observation_dv.resource_type = "Observation"
#         observation_dv.id = "dv-"+dvuid
#         observation_dv.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-variant"]})
#         observation_dv.status = "final"
#         observation_dv.category = [concept.CodeableConcept({"coding":[{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]})]
#         observation_dv.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"69548-6","display":"Genetic variant assessment"}]})
#         observation_dv.subject = patient_reference
#         observation_dv.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"LA9633-4","display":"present"}]})

#         observation_dv_component1 = observation.ObservationComponent()
#         observation_dv_component1.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "62374-4","display": "Human reference sequence assembly version"}]})
#         observation_dv_component1.valueCodeableConcept = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "LA14029-5","display": "GRCh37"}]})

#         observation_dv_component2 = observation.ObservationComponent()
#         observation_dv_component2.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "48013-7","display": "Genomic reference sequence ID"}]})
#         observation_dv_component2.valueCodeableConcept = concept.CodeableConcept({"coding": [{"system": "http://www.ncbi.nlm.nih.gov/nuccore","code": refSeq}]})

#         observation_dv_component3 = observation.ObservationComponent()
#         observation_dv_component3.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "53034-5","display": "Allelic state"}]})
#         observation_dv_component3.valueCodeableConcept = concept.CodeableConcept({"coding": [{"system": "http://loinc.org"}]})

#         observation_dv_component4 = observation.ObservationComponent()
#         observation_dv_component4.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "69547-8","display": "Genomic Ref allele"}]})
#         observation_dv_component4.valueString = alleles.at[index,'REF']

#         observation_dv_component5 = observation.ObservationComponent()
#         observation_dv_component5.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "69551-0","display": "Genomic Alt allele"}]})
#         observation_dv_component5.valueString = alleles.at[index,'ALT']

#         observation_dv_component6 = observation.ObservationComponent()
#         observation_dv_component6.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "tbd-coordinate system","display": "Genomic coordinate system"}]})
#         observation_dv_component6.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/genetic-coordinate-system","code":"1"}]})

#         observation_dv_component7 = observation.ObservationComponent()
#         observation_dv_component7.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "81254-5","display": "Genomic Allele start-end"}]})

#         observation_dv.component =  [observation_dv_component1,observation_dv_component2,observation_dv_component3,observation_dv_component4,observation_dv_component5,observation_dv_component6,observation_dv_component7]
#         obsContained.append(observation_dv)

#     # Obesrvation structure: sequence-phase relatons
#     siduids = []

#     for index in sequenceRels.index:
#         dvRef1 = dvuids.get(str(sequenceRels.at[index,'POS1']))
#         dvRef2 = dvuids.get(str(sequenceRels.at[index,'POS2']))
#         siduid = uuid4().hex[:13]
#         siduids.append(siduid)

#         observation_sid = observation.Observation()
#         observation_sid.resource_type = "Observation"
#         observation_sid.id = "sid-"+siduid
#         observation_sid.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-sequence-phase-reltn"]})
#         observation_sid.status = "final"
#         observation_sid.category = [concept.CodeableConcept({"coding":[{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]})]
#         observation_sid.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"82120-7","display":"Sequence phase relationship"}]})
#         observation_sid.subject = patient_reference
#         observation_sid.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"TBD-cisTrans","display":sequenceRels.at[index,'Relation']}]})
#         obsContained.append(observation_sid)

#     report.contained = obsContained

#     reportResult = [variant_reference]
#     for pos,uid in dvuids.items():
#         reportResult.append(reference.FHIRReference({"reference": "#dv-"+uid}))

#     for uid in siduids:
#         reportResult.append(reference.FHIRReference({"reference": "#sid-"+uid}))
    
#     report.result = reportResult

#     response = report.as_json()
#     od = OrderedDict() 
#     od["resourceType"] = response['resourceType']
#     od["id"] = response['id']
#     od["meta"] = response['meta']
#     od["contained"] = response['contained']
#     od["status"] = response['status']
#     od["code"] = response['code']
#     od["subject"] = response['subject']
#     od["issued"] = response['issued']
#     od["result"] = response['result']

#     sidIndex = 0
#     for index,fhirReport in enumerate(od['contained']):
#         if (fhirReport['id'].startswith('sid-')):
#             sidIndex = index
#             break
#     z=1
#     q=2

#     for index,(sequenceRel, fhirReport) in enumerate(zip(sequenceRels.index, od['contained'][sidIndex:])):
#         dvRef1 = dvuids.get(str(sequenceRels.at[index,'POS1']))
#         dvRef2 = dvuids.get(str(sequenceRels.at[index,'POS2']))
#         if (fhirReport['id'].startswith('sid-')):
#             derivedFromDV1 = {}
#             derivedFromDV2 = {}
#             derivedFromDV1['reference'] = "#dv-"+dvRef1
#             derivedFromDV2['reference'] = "#dv-"+dvRef2
#             derivedFrom = [derivedFromDV1,derivedFromDV2]
#             fhirReport['derivedFrom']= derivedFrom

#     for k,i in  enumerate(od['contained']):
#         if (i['id'].startswith('rs-')):
#             odRS = OrderedDict() 
#             odRS["resourceType"] = i['resourceType']
#             odRS["id"] = i['id']
#             odRS["meta"] = i['meta']
#             odRS["status"] = i['status']
#             odRS["category"] = i['category']
#             odRS["code"] = i['code']
#             odRS["subject"] = i['subject']
#             odRS["component"] = i['component']
#             od['contained'][k] = odRS

#         if (i['id'].startswith('dv-')):
#             odDV = OrderedDict() 
#             odDV["resourceType"] = i['resourceType']
#             odDV["id"] = i['id']
#             odDV["meta"] = i['meta']
#             odDV["status"] = i['status']
#             odDV["category"] = i['category']
#             odDV["code"] = i['code']
#             odDV["subject"] = i['subject']
#             odDV["valueCodeableConcept"] = i['valueCodeableConcept']
#             odDV["component"] = i['component']
#             od['contained'][k] = odDV

#         if (i['id'].startswith('sid-')):
#             odSID = OrderedDict() 
#             odSID["resourceType"] = i['resourceType']
#             odSID["id"] = i['id']
#             odSID["meta"] = i['meta']
#             odSID["status"] = i['status']
#             odSID["category"] = i['category']
#             odSID["code"] = i['code']
#             odSID["subject"] = i['subject']
#             odSID["valueCodeableConcept"] = i['valueCodeableConcept']
#             odSID["derivedFrom"] = i['derivedFrom']

#             od['contained'][k] = odSID
    
#     with open(FHIR_JSON_RESULT+'fhir.json', 'w') as fhirJSON:

#         fhirJSON.write(json.dumps(od))
#     return FHIR_JSON_RESULT

def getFhirJSON(cleanVcf,nextelem,patientID,refSeq,noCall=False,gender="M"):
    
    dvuids = {}
    siduids = []

    alleles = getAllelicState(cleanVcf,nextelem,gender)
    logging.info(alleles)
    sequenceRels = getSequenceRelation(cleanVcf,nextelem)

    noCallRegion,queryRange = getNoCallableData(NO_CALL_FILE,QUERY_RANGE_FILE)
    nocallRows = len(noCallRegion.index)
    start = queryRange.at[0,"START"]
    end = queryRange.at[0,"END"]

    if not noCallRegion.empty:
        if noCallRegion['START'].iloc[0] <= queryRange['START'].iloc[0]:
            noCallRegion['START'].iloc[0] = queryRange['START'].iloc[0]

        if noCallRegion['END'].iloc[-1] >= queryRange['END'].iloc[0]:
            noCallRegion['END'].iloc[-1] = queryRange['END'].iloc[0]
    else:
        noCall = False

    contained_uid = uuid4().hex[:13]
    patient_reference = reference.FHIRReference({"reference":"Patient/"+patientID})
    variant_reference = reference.FHIRReference({"reference": "#rs-"+contained_uid})

    report = dr.DiagnosticReport()
    report.id = "dr-"+uuid4().hex[:13]
    report.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/genomics-report"]})
    report.status = "final"
    report.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"81247-9","display":"Master HL7 genetic variant reporting panel"}]})
    report.subject = patient_reference
    report.issued = date.FHIRDate(Utilities.getFhirDate())

    observation_rs = observation.Observation()
    contained_rs = observation_rs
    
    contained_rs.id = "rs-"+contained_uid
    observation_rs.resource_type = "Observation"
    contained_rs.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/region-studied"]})
    observation_rs.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"53041-0","display":"DNA region of interest panel"}]})
    observation_rs.status = "final"
    observation_rs.category = [concept.CodeableConcept({"coding":[{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]})]
    observation_rs.subject = patient_reference
    observation_rs_component1 = observation.ObservationComponent()
    observation_rs_component1.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "51959-5","display": "Range(s) of DNA sequence examined"}]})

    observation_rs_component2 = observation.ObservationComponent()
    observation_rs_component2.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "92822-6","display": "Genomic coord system"}]})
    observation_rs_component2.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"LA30102-0","display": "1-based character counting"}]})

    observation_rs_component3 = observation.ObservationComponent()
    observation_rs_component3.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "48013-7","display": "Genomic reference sequence ID"}]})
    observation_rs_component3.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://www.ncbi.nlm.nih.gov/nuccore","code":refSeq}]})

    if noCall:
        #component Region-studied (No call region)
        nocallComponents = []
        for i in range (nocallRows):
            nocallComponents.append('observation_rs_component'+str(i+4))

        observation_rs_components = []
        for (index, i) in zip(noCallRegion.index, nocallComponents):
            i = observation.ObservationComponent()
            i.code = concept.CodeableConcept({"coding": [{ "system": "http://loinc.org","code": "TBD-noCallRegion","display": "No call region"}]})
            observation_rs_components.append(i)
        observation_rs.component = [observation_rs_component1,observation_rs_component2,observation_rs_component3] + observation_rs_components
    else:

        observation_rs.component = [observation_rs_component1,observation_rs_component2,observation_rs_component3]

    # Observation structure : described-variants
    obsContained = [contained_rs]
    for index in alleles.index:
        # import pdb;pdb.set_trace()
        dvuid = uuid4().hex[:13]
        dvuids.update({ str(alleles.at[index,'POS']) : dvuid})

        observation_dv = observation.Observation()

        observation_dv = observation.Observation()
        observation_dv.resource_type = "Observation"
        observation_dv.id = "dv-"+dvuid
        observation_dv.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/variant"]})
        observation_dv.status = "final"
        observation_dv.category = [concept.CodeableConcept({"coding":[{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]})]
        observation_dv.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"69548-6","display":"Genetic variant assessment"}]})
        observation_dv.subject = patient_reference
        observation_dv.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"LA9633-4","display":"present"}]})

        observation_dv_component1 = observation.ObservationComponent()
        observation_dv_component1.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "62374-4","display": "Human reference sequence assembly version"}]})
        observation_dv_component1.valueCodeableConcept = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "LA14029-5","display": "GRCh37"}]})

        observation_dv_component2 = observation.ObservationComponent()
        observation_dv_component2.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "48013-7","display": "Genomic reference sequence ID"}]})
        observation_dv_component2.valueCodeableConcept = concept.CodeableConcept({"coding": [{"system": "http://www.ncbi.nlm.nih.gov/nuccore","code": refSeq}]})

        observation_dv_component3 = observation.ObservationComponent()
        observation_dv_component3.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "53034-5","display": "Allelic state"}]})
        observation_dv_component3.valueCodeableConcept = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": alleles.at[index,'CODE'],"display": alleles.at[index,'ALLELE']}]})        

        observation_dv_component4 = observation.ObservationComponent()
        observation_dv_component4.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "69547-8","display": "Genomic Ref allele [ID]"}]})
        observation_dv_component4.valueString = alleles.at[index,'REF']

        observation_dv_component5 = observation.ObservationComponent()
        observation_dv_component5.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "69551-0","display": "Genomic Alt allele [ID]"}]})
        observation_dv_component5.valueString = alleles.at[index,'ALT']

        observation_dv_component6 = observation.ObservationComponent()
        observation_dv_component6.code = concept.CodeableConcept({"coding": [{"system": "http://loinc.org","code": "92822-6","display": "Genomic coord system"}]})
        observation_dv_component6.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"LA30102-0","display":"1-based character counting"}]})

        observation_dv_component7 = observation.ObservationComponent()
        observation_dv_component7.code = concept.CodeableConcept({"coding": [{"system": "http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/tbd-codes","code": "exact-start-end","display": "Variant exact start and end"}]})

        observation_dv.component =  [observation_dv_component1,observation_dv_component2,observation_dv_component3,observation_dv_component4,observation_dv_component5,observation_dv_component6,observation_dv_component7]
        obsContained.append(observation_dv)

    # Obesrvation structure: sequence-phase relatons
    siduids = []

    for index in sequenceRels.index:
        dvRef1 = dvuids.get(str(sequenceRels.at[index,'POS1']))
        dvRef2 = dvuids.get(str(sequenceRels.at[index,'POS2']))
        siduid = uuid4().hex[:13]
        siduids.append(siduid)

        observation_sid = observation.Observation()
        observation_sid.resource_type = "Observation"
        observation_sid.id = "sid-"+siduid
        observation_sid.meta = meta.Meta({"profile":["http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/sequence-phase-relationship"]})
        observation_sid.status = "final"
        observation_sid.category = [concept.CodeableConcept({"coding":[{"system": "http://terminology.hl7.org/CodeSystem/observation-category","code": "laboratory"}]})]
        observation_sid.code = concept.CodeableConcept({"coding":[{"system":"http://loinc.org","code":"82120-7","display":"Allelic phase"}]})
        observation_sid.subject = patient_reference
        observation_sid.valueCodeableConcept = concept.CodeableConcept({"coding":[{"system":"http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/seq-phase-relationship","code":sequenceRels.at[index,'Relation'],"display":sequenceRels.at[index,'Relation']}]})
        obsContained.append(observation_sid)

    report.contained = obsContained

    reportResult = [variant_reference]
    for pos,uid in dvuids.items():
        reportResult.append(reference.FHIRReference({"reference": "#dv-"+uid}))

    for uid in siduids:
        reportResult.append(reference.FHIRReference({"reference": "#sid-"+uid}))
    
    report.result = reportResult
    response = report.as_json()


    od = OrderedDict() 
    od["resourceType"] = response['resourceType']
    od["id"] = response['id']
    od["meta"] = response['meta']
    od["contained"] = response['contained']
    od["status"] = response['status']
    od["code"] = response['code']
    od["subject"] = response['subject']
    od["issued"] = response['issued']
    od["result"] = response['result']

    odCodeCoding = OrderedDict()
    odCodeCoding["system"] = od["code"]["coding"][0]["system"]
    odCodeCoding["code"] = od["code"]["coding"][0]["code"]
    odCodeCoding["display"] = od["code"]["coding"][0]["display"]
    od["code"]["coding"][0] = odCodeCoding

    sidIndex = 0
    for index,fhirReport in enumerate(od['contained']):
        if (fhirReport['id'].startswith('sid-')):
            sidIndex = index
            break

    for index,(sequenceRel, fhirReport) in enumerate(zip(sequenceRels.index, od['contained'][sidIndex:])):
        dvRef1 = dvuids.get(str(sequenceRels.at[index,'POS1']))
        dvRef2 = dvuids.get(str(sequenceRels.at[index,'POS2']))
        if (fhirReport['id'].startswith('sid-')):
            derivedFromDV1 = {}
            derivedFromDV2 = {}
            derivedFromDV1['reference'] = "#dv-"+dvRef1
            derivedFromDV2['reference'] = "#dv-"+dvRef2
            derivedFrom = [derivedFromDV1,derivedFromDV2]
            fhirReport['derivedFrom']= derivedFrom

    for k,i in  enumerate(od['contained']):
        if (i['category'][0]['coding'][0]):
            odCategoryCoding = OrderedDict()
            odCategoryCoding["system"] = i['category'][0]['coding'][0]["system"] 
            odCategoryCoding["code"] = i['category'][0]['coding'][0]["code"] 
            od['contained'][k]['category'][0]['coding'][0]  = odCategoryCoding

        if (i['code']['coding'][0]):
            odCodeCoding = OrderedDict()
            odCodeCoding["system"] = i['code']['coding'][0]["system"] 
            odCodeCoding["code"] = i['code']['coding'][0]["code"]
            odCodeCoding["display"] = i['code']['coding'][0]["display"]
            od['contained'][k]['code']['coding'][0]  = odCodeCoding
        
        if 'valueCodeableConcept' in i.keys():
            odValueCodeableConceptCoding = OrderedDict()
            odValueCodeableConceptCoding["system"] = i['valueCodeableConcept']['coding'][0]["system"] 
            odValueCodeableConceptCoding["code"] = i['valueCodeableConcept']['coding'][0]["code"]
            odValueCodeableConceptCoding["display"] = i['valueCodeableConcept']['coding'][0]["display"]
            od['contained'][k]['valueCodeableConcept']['coding'][0] =  odValueCodeableConceptCoding

        if ((i['id'].startswith('dv-')) or (i['id'].startswith('rs-'))):
            for l,j in enumerate(i['component']):
                odComponentCodeCoding = OrderedDict()
                if j['code']['coding'][0]["system"]:
                    odComponentCodeCoding["system"] = j['code']['coding'][0]["system"] 
                if j['code']['coding'][0]["code"]:
                    odComponentCodeCoding["code"] = j['code']['coding'][0]["code"]
                if j['code']['coding'][0]["display"]:
                    odComponentCodeCoding["display"] = j['code']['coding'][0]["display"]
                if od['contained'][k]['component'][l]['code']['coding'][0]:
                    od['contained'][k]['component'][l]['code']['coding'][0] = odComponentCodeCoding

                odComponentvalueCodeableConcept = OrderedDict()
                if 'valueCodeableConcept' in  j.keys():
                    odComponentvalueCodeableConcept["system"] = j['valueCodeableConcept']['coding'][0]["system"] 
                    if 'code' in j['valueCodeableConcept']['coding'][0].keys():
                        odComponentvalueCodeableConcept["code"] = j['valueCodeableConcept']['coding'][0]["code"]
                    if 'display' in j['valueCodeableConcept']['coding'][0].keys():
                        odComponentvalueCodeableConcept["display"] = j['valueCodeableConcept']['coding'][0]["display"]
                    od['contained'][k]['component'][l]['valueCodeableConcept']['coding'][0] = odComponentvalueCodeableConcept


        if (i['id'].startswith('rs-')):
            odRS = OrderedDict() 
            odRS["resourceType"] = i['resourceType']
            odRS["id"] = i['id']
            odRS["meta"] = i['meta']
            odRS["status"] = i['status']
            odRS["category"] = i['category']
            odRS["code"] = i['code']
            odRS["subject"] = i['subject']
            odRS["component"] = i['component']
            od['contained'][k] = odRS

        if (i['id'].startswith('dv-')):
            odDV = OrderedDict() 
            odDV["resourceType"] = i['resourceType']
            odDV["id"] = i['id']
            odDV["meta"] = i['meta']
            odDV["status"] = i['status']
            odDV["category"] = i['category']
            odDV["code"] = i['code']
            odDV["subject"] = i['subject']
            odDV["valueCodeableConcept"] = i['valueCodeableConcept']
            odDV["component"] = i['component']
            od['contained'][k] = odDV

        if (i['id'].startswith('sid-')):
            odSID = OrderedDict() 
            odSID["resourceType"] = i['resourceType']
            odSID["id"] = i['id']
            odSID["meta"] = i['meta']
            odSID["status"] = i['status']
            odSID["category"] = i['category']
            odSID["code"] = i['code']
            odSID["subject"] = i['subject']
            odSID["valueCodeableConcept"] = i['valueCodeableConcept']
            odSID["derivedFrom"] = i['derivedFrom']
            od['contained'][k] = odSID
    with open(FHIR_JSON_RESULT+'fhir.json', 'w') as fhirJSON:
        fhirJSON.write(json.dumps(od))
    
    return FHIR_JSON_RESULT