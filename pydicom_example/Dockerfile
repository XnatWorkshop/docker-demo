# Build a dcmstack compatible Docker image with preloaded dcm->nii script.
FROM python:2.7.11
RUN pip install requests
RUN easy_install pydicom
RUN pip install nibabel
RUN wget https://github.com/moloney/dcmstack/archive/master.zip
RUN easy_install master.zip
RUN mkdir /scripts
RUN wget -q https://raw.githubusercontent.com/XnatWorkshop/docker-demo/master/pydicom_example/dicom2nifti_rest.py -O /scripts/pydicom.py
