# third-party packages
import boto3
import requests

# builtin python packages
import json
import os
import sys


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', 'https://objets.juno.calculquebec.ca')
GENEYX_API_URL = os.environ.get('GENEYX_API_URL', 'https://analysis.geneyx.com/api/updateSample')
GENEYX_API_USER_ID = os.environ.get('GENEYX_API_USER_ID')
GENEYX_API_USER_KEY = os.environ.get('GENEYX_API_USER_KEY')

PACBIO_DATA_BUCKET =  os.environ.get('PACBIO_DATA_BUCKET','decodeur-pacbio')


def generate_presigned_url(s3_client, bucket_name, object_key, expiration=3600):
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
    print(file)
    with open(file, 'r') as stream:
        try:
            data = json.load(stream)            
            return data
        except KeyError as exc:
            print(exc)

def main():
    s3_client = boto3.client(
        service_name='s3',
        endpoint_url= AWS_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    example_nameList=["MP-XX-XXXXX","FM-XX-XXXXX"]
    for sample_name in example_nameList:
        bucket_name = PACBIO_DATA_BUCKET
        # BAM and BAI files are in the same folder
        base_folder = f"S3-Storage/{sample_name}/"
        bam_file = f"{base_folder}{sample_name}.haplotagged.bam"
        bai_file = f"{base_folder}{sample_name}.haplotagged.bam.bai"
        #methyl_file = f"{base_folder}{sample_name}.GRCh38.hap1.bw"
        # Generate a presigned URL for the BAM file
        #print(f"Generating presigned URL for BAM file: {bam_file}")
        bam_url = generate_presigned_url(s3_client, bucket_name, bam_file, expiration=600)
        bai_url = generate_presigned_url(s3_client, bucket_name, bai_file, expiration=600)
        #methyl_url = generate_presigned_url(bucket_name, methyl_file, expiration=6000)
        if bam_url and bai_url:
            print("Presigned URL for BAM file:")
            combined_url=f"{bam_url}$${bai_url}"
            print(combined_url)
            #print("Methylation URL:")
            #print(methyl_url)
        else:
            print(f"Failed to generate presigned URL for {sample_name}")
            sys.exit(1)

        vcfName=sample_name+".GRCh38.deepvariant.phased.vcf.gz"
        jsonDict={"ApiUserID": GENEYX_API_USER_ID,\
        "ApiUserKey": GENEYX_API_USER_KEY,\
        "BamUrl": combined_url,\
        "SerialNumber": vcfName}
        with open('updateURL.json', 'w') as fp:
            jsonFile=json.dump(jsonDict,fp)
        data=loadDataJson("updateURL.json")
        api = GENEYX_API_URL
        print(f"Updating {sample_name}")
        r = requests.post(api, json=jsonDict)
        print(r)
        print(r.content)


if __name__ == "__main__":
    main()