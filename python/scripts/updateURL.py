# third-party packages
import boto3
import requests
from dotenv import load_dotenv 

# builtin python packages
import json
import os
import sys

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL', 'https://objets.juno.calculquebec.ca')
GENEYX_API_URL = os.getenv('GENEYX_API_URL', 'https://analysis.geneyx.com/api/updateSample')
GENEYX_API_USER_ID = os.getenv('GENEYX_API_USER_ID')
GENEYX_API_USER_KEY = os.getenv('GENEYX_API_USER_KEY')
PACBIO_DATA_BUCKET =  os.getenv('PACBIO_DATA_BUCKET','decodeur-pacbio')

def generate_presigned_url(s3_client,bucket_name, object_key, expiration=3600):
    """
    Generate a presigned URL for accessing a file in an S3-compatible storage.
    """
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration,
            HttpMethod='GET'
        )
        return response
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None


def loadDataJson(file):
    with open(file, 'r') as stream:
        try:
            data = json.load(stream)            
            return data
        except KeyError as exc:
            print(exc)
def main():
    s3_client = boto3.client(
        service_name='s3',
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,)

    if len(sys.argv) < 2:
        print("Usage: python script.py <sample_name_list>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        nameList = f.read().splitlines()

    errorList=[]
    for nameline in nameList:
        sample_name = nameline.split(",")[0]
        version = nameline.split(",")[1]
        bucket_name = PACBIO_DATA_BUCKET

        #2 possibilities for version:
        #- Version is the name of the vcf directly
        #- Version follows trioName/Role/vcfName (ex p001/Proband/XXX.vcf, p022/Father/YYY.vcf)
        #   which is a different VCF and path format for joint calls
        if "/" in version and ("proband" in version or "mother" in version or "father" in version):
            trioName = version.split("/")[0]
            role = version.split("/")[1]
            vcfName= version.split("/")[2]
            base_folder = f"S3-Storage/{trioName}/{role}/"
        else:
            vcfName = version
            base_folder = f"S3-Storage/{sample_name}/"


        # BAM and BAI files are in the same folder
        bam_file = f"{base_folder}{sample_name}.haplotagged.bam"
        bai_file = f"{base_folder}{sample_name}.haplotagged.bam.bai"
        methyl_file = f"{base_folder}{sample_name}.GRCh38.cpg_pileup.combined.bed.gz"
        methyl_index = f"{base_folder}{sample_name}.GRCh38.cpg_pileup.combined.bed.gz.tbi"        
        # Generate a presigned URL for the BAM file
        bam_url = generate_presigned_url(s3_client,bucket_name, bam_file, expiration=86400)
        bai_url = generate_presigned_url(s3_client,bucket_name, bai_file, expiration=86400)
        methyl_url = generate_presigned_url(s3_client,bucket_name, methyl_file, expiration=6048000)
        methyl_index_url = generate_presigned_url(s3_client,bucket_name, methyl_index, expiration=6048000)
        if bam_url and bai_url:
            combined_url=f"{bam_url}$${bai_url}"
            print(combined_url)
            combined_methyl=f"{methyl_url}$${methyl_index_url}"
        else:
            print(f"Failed to generate presigned URL for {sample_name}")
            sys.exit()

        jsonDict={"ApiUserID": GENEYX_API_USER_ID,\
        "ApiUserKey": GENEYX_API_USER_KEY,\
        "BamUrl": combined_url,\
        "MethylationUrl": combined_methyl,\
        "SerialNumber": vcfName}

        with open('updateURL.json', 'w') as fp:
            jsonFile=json.dump(jsonDict,fp)
        data=loadDataJson("updateURL.json")
        api = GENEYX_API_URL
        r = requests.post(api, json=data)
        code = r.json()
        if "error" in code["Code"] :
            errorList.append(sample_name)
            print(f"{sample_name} failed to send")
            print(code)

    if len(errorList) == len(nameList):
        print("All samples failed to be sent")
    elif len(errorList) > 0:
        print("Some samples could not be sent successfully:")
        for name in errorList: print(name)
    else:
        print("All samples sent successfully")

if __name__ == "__main__":
    main()