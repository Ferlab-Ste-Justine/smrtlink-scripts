# smrtlink-scripts

This directory will contain scripts and files related to creating images related to data transfers between the smrtlink sequencer server, narval, our decodeur-pacbio S3 bucket and the GeneYX platform. 

For a description of the dockerfile and how to run and update the scripts, see the [readme](https://github.com/Ferlab-Ste-Justine/smrtlink-scripts/blob/main/python/README.md). 

Here is a list of the scripts:
- updateURL.py

### updateURL.py
This script is used to generate temporary 24h URLs to our BAM and methylation files currently stored on our s3 bucket. For each sample, the script will also push the generated URLs to GeneYX, a data-visualization platform. 
The URL for the index of both the BAM and the methylation files also need to be concatenated to be accessible on GeneYX. 
The goal is to prevent unauthorized access of potentially identifying information through a non-expiring BAM URL, while keeping the data accessible to our analysts on GeneYX. We expect to run this script every day automatically, 

Requirements:
As described [here](https://github.com/Ferlab-Ste-Justine/smrtlink-scripts/blob/main/python/README.md#running-the-updateurlpy-script), this script requires environment variables for key ID and access, both for the s3 bucket and the GeneYX account. 
A second requirement is to include a file as argument containing the sample names and their path version on GeneYX, separated by comma. A version of "1" corresponds to samples using the format "{sample_name}.GRCh38.deepvariant.phased.vcf.gz" on GeneYX, and the version "2" corresponds to: "{sample_name}.GRCh38.small_variants.phased.vcf.gz".
The input file will use a format like the following:

```
sample_1,1
sample_2,1
sample_3,2
```
The script will print the combined URL of BAM and methylation files for all samples, along with a code of "success" or "{sample_name} failed to send". 
Once all the files are processed, a list of the samples that failed to send is printed. 
