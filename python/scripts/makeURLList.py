# third-party packages
import boto3
from dotenv import load_dotenv 
from updateURL import generate_presigned_url
# builtin python packages
import json
import os
import sys

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL', 'https://objets.juno.calculquebec.ca')
PACBIO_DATA_BUCKET =  os.getenv('PACBIO_DATA_BUCKET','decodeur-pacbio')

#This script will need a sample name list as input, in the format of "trio_name,decodeur_id" per line. 
# It will generate a JSON list of presigned URLs called decodeurURL.json 
# for the BAM files, methylation files and haplotype files,
# The URLs will be valid for 10 days (864000 seconds).

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

    if os.path.exists('decodeurURL.json'):
        os.remove('decodeurURL.json')

    url_dict = {}
    for nameline in nameList:
        parts = nameline.split(",")
        if len(parts) < 2:
            print(f"Skipping malformed line (expected 'trio_name,decodeur_id'): {nameline!r}")
            continue
        trio_name = parts[0]
        print(trio_name)
        decodeur_id = parts[1]
        bucket_name = PACBIO_DATA_BUCKET

        # The base folder depends on the role of the sample, found in the decodeur_id
        if decodeur_id.endswith("03"):
            role = "proband"
        elif decodeur_id.endswith("02"):
            role = "mother"
        elif decodeur_id.endswith("01"):
            role = "father"
        else:
            print(f"Could not infer family role of Sample {decodeur_id}, skipping.")
            continue
        base_folder = f"S3-Storage/{trio_name}/{role}/"
        
        # BAM and BAI files are in the same folder
        bam_file = f"{base_folder}{decodeur_id}.haplotagged.bam"
        bai_file = f"{base_folder}{decodeur_id}.haplotagged.bam.bai"
        methyl_file = f"{base_folder}{decodeur_id}.GRCh38.cpg_pileup.combined.bed.gz"
        methyl_index = f"{base_folder}{decodeur_id}.GRCh38.cpg_pileup.combined.bed.gz.tbi"
        hap1_file = f"{base_folder}{decodeur_id}.GRCh38.cpg_pileup.hap1.bed.gz"
        hap1_index = f"{base_folder}{decodeur_id}.GRCh38.cpg_pileup.hap1.bed.gz.tbi"
        hap2_file = f"{base_folder}{decodeur_id}.GRCh38.cpg_pileup.hap2.bed.gz"
        hap2_index = f"{base_folder}{decodeur_id}.GRCh38.cpg_pileup.hap2.bed.gz.tbi"

        # Generate a presigned URL for the BAM file, BAI file, methylation files and haplotype files
        #We allow a longer expiration time for this list, 10 days
        bam_url = generate_presigned_url(s3_client,bucket_name, bam_file, expiration=864000)
        bai_url = generate_presigned_url(s3_client,bucket_name, bai_file, expiration=864000)
        methyl_url = generate_presigned_url(s3_client,bucket_name, methyl_file, expiration=864000)
        methyl_index_url = generate_presigned_url(s3_client,bucket_name, methyl_index, expiration=864000)
        hap1_url = generate_presigned_url(s3_client,bucket_name, hap1_file, expiration=864000)
        hap1_index_url = generate_presigned_url(s3_client,bucket_name, hap1_index, expiration=864000)
        hap2_url = generate_presigned_url(s3_client,bucket_name, hap2_file, expiration=864000)
        hap2_index_url = generate_presigned_url(s3_client,bucket_name, hap2_index, expiration=864000)
        if not bam_url or not bai_url or not methyl_url or not methyl_index_url or not hap1_url or not hap1_index_url or not hap2_url or not hap2_index_url:
            print(f"Failed to generate presigned URL for {trio_name} {role}")
            sys.exit(1)

        url_dict[decodeur_id] = {
        "bam_url": bam_url,
        "bai_url": bai_url,
        "methyl_combined_url": methyl_url,
        "methyl_combined_index_url": methyl_index_url,
        "methyl_hap1_url": hap1_url,
        "methyl_hap1_index_url": hap1_index_url,
        "methyl_hap2_url": hap2_url,
        "methyl_hap2_index_url": hap2_index_url
        }
        print(url_dict[decodeur_id])

    with open('decodeurURL.json', 'w') as fp:
        json.dump(url_dict,fp)

    print(f"Generated URL list decodeurURL.json for {len(url_dict)} samples")

if __name__ == "__main__":
    main()
