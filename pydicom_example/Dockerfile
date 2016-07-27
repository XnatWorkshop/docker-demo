# Build a dcmstack compatible Docker image with preloaded dcm->nii script.
FROM python:2.7.11
RUN pip install requests
RUN easy_install pydicom
RUN pip install nibabel
RUN wget https://github.com/moloney/dcmstack/archive/master.zip && easy_install master.zip
RUN mkdir /scripts
COPY dicom2nifti_rest.py /scripts/pydicom.py
LABEL "org.nrg.commands"="[{\"name\":\"pydicom\",\"description\":\"Converts dicom to nifti with pydicom. Runs on a session; uploads nifti back to each scan manually.\", \"mounts-in\":[{\"name\":\"root\", \"remote-path\":\"/data/input\"}], \"mounts-out\":[{\"name\":\"NIFTI\", \"remote-path\":\"/data/output\"}], \"run-template\":[\"/bin/bash\", \"-c\", \"python /scripts/pydicom.py -h \$XNAT_HOST -u \$XNAT_USER -p \$XNAT_PASS -s #sessionId#\"],\"variables\":[{\"name\":\"sessionId\", \"description\": \"XNAT ID of session on which we are running\", \"required\":true, \"root-property\":\"ID\"}]}]"
