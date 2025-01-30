# Dockerfile Description

This Dockerfile is used to create a simple Python Docker image to run various scripts (see the scripts folder) related to PacBio file URLs management. 

For example, the updateUrl.py script obtains new 24-hour valid links for a set of BAM files and pushes them to Geneyx. 
Other scripts performing related or similar tasks may be added in the future.

## Use the image

Once the image is built, here are example commands that you can use to execute a script.

### Running the `updateUrl.py` Script

First create a .env file with required environment variables for the script:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_ENDPOINT_URL=https://objets.juno.calculquebec.ca
GENEYX_API_URL=https://analysis.geneyx.com/api/updateSample
GENEYX_API_USER_ID=your_user_id
GENEYX_API_USER_KEY=your_user_key
PACBIO_DATA_BUCKET=decodeur-pacbio
```

Then run the docker container. 
Here we assume that you want to pass the file `your_input_folder/input.txt` as input to the script.

```
docker run --rm --env-file .venv  -v your_input_folder:/data ferlabcrsj/smrtlink-scripts:1.0.0 python updateURL.py /data/input.txt
```

Here are details about the different parts of this command:
- `--rm`: Automatically remove the container when it exists.
- `--env-file .env`: Loads environment variables from the `.env` file in the container.
- `-v your_input_folder:/data`: Mounts the `your_input_folder` directory from the host to the container at `/data`.
- `ferlabcrsj/smrtlink-scripts:1.0.0`: The name and tag of the docker image.
- `python updateURL.py /data/input.txt`: The command to run on the container

## Automatic image build via github actions

The docker image is automatically built and pushed to the ferlab docker registry (dockerhub/ferlabcrsj) using github actions. 

The build process is triggered when:
-  Pull requests are merged into the main branch
-  Git tags (in semver format) are pushed to the repository

 Depending on the event that triggered the build, different tags are associated to the docker image.  
- **Semantic Versioning Tag (semver)**:
   When a git tag in semver format is pushed to the repository the docker image tag will match the git tag. For example, pushing the git tag `v1.0.0` will result in a new docker image tagged as `ferlabcrsj/smrtlink-scripts:1.0.0`. Note that only semver tags are supported, which means the tag format must be `vX.Y.Z`.
 - **Latest tag**:
   When a pull request is merged into the main branch, the image is rebuilt with the tag `latest`, i.e. `ferlabcrsj/smrtlink-scripts:latest`. So this image always match the Dockerfile on the main branch.
- **Commit SHA Tag**:
   A new image with the commit sha as the tag is also created when a pull request is merged into the main branch  (ex: `ferlabcrsj:smrtlink-scripts/cca9acc45e40b96374312b80e3e99af49991ec6e`).

To create and push a new git tag, you can use the following commands:

```
git checkout main
git pull
git tag <tagname>
git push origin <tagname>
```

The tag name must follow the semver format, specifically `vX.Y.Z` where `X`, `Y` and `Z` are integers. For example: `v1.0.0`.

## Build the image locally

Here is an example command that you can use to build the Docker image locally. 
Run this command from the root of the smrtlink-scripts repository. 
You can use any image name and tag of your choice:

```
docker build -t ferlabcrsj/smrtlink-scripts:dev  -f python/Dockerfile  python
```

## Update python dependencies

We have two files for managing dependencies: `requirements_minimal.txt` and `requirements_full.txt`.
- `requirements_full.txt` contains the complete list of packages along with their associated versions. This file is used in the Dockerfile when building the image.
- `requirements_minimal.txt` contains only dependencies that are directly required by the project, without including their transitive dependencies. 
   The `requirements_full.txt` file is generated from this file.


Procedure to add a new python dependency:
1) Add the new dependency to `requirements_minimal.txt`. You can specify a version number if needed.
2) Run the following command from the root of the repository to update `requirements_full.txt` from `requirements_minimal.txt`:

```
docker run -it --rm  -v ./python:/tmp  python:3.10.12-slim  /bin/bash -c  'pip install --upgrade pip && pip install -r /tmp/requirements_minimal.txt && pip freeze > /tmp/requirements_full.txt'
```

3) Make sure to commit and push your changes

The next time you will build the image, it will use the new requirements_full.txt file
to install dependencies.