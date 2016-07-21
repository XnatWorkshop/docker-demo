# /bin/env python

# Converts a directory of one or more DICOM files into the NIfTI format
# Primary use is to test the XNAT Docker service.
# Input directory is assumed to be /data/input
#   Input directory format is assumed to be /data/input/SCANS/{scan_id}/DICOM/
# Output directory is assumed to be /data/output
#   Output directory format will be generated as /data/output/SCANS/{scan_id}/NIFTI/


# USAGE: python pyscript.py -h <hostname> -u <user> -p <password> -s <session_id>

import sys
import os
import dcmstack
import getopt
import requests
from glob import glob


def main(argv):
    host = ''  # 'https://central.xnat.org'
    user = ''  # 'be3e56eb-8a49-4e76-9cc7-c7c19ae65ca8'
    password = ''  # '1458595180760'
    session = ''  # 'CENTRAL_E07096'

    try:
        opts, args = getopt.getopt(argv, "h:u:p:s:", ["host=", "user=", "password=", "session="])
    except getopt.GetoptError:
        print 'pyscript.py -h <hostname> -u <user> -p <password> -s <session_id>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host = arg
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-s", "--session"):
            session = arg

    input_dir = '/data/input'
    output_dir = '/data/output'

    # parse input directory structure by scan id
    for scan, dcm in get_scan_sets(input_dir).iteritems():
        # use dcmstack to create a nifti file from each scan set
        nifit_file_name = output_dir + os.path.sep + scan + '.nii.gz';
        dcm_to_nii(dcm, nifit_file_name)
        # post nii.gz file to NIFTI folder on host
        #post_nifti(host, user, password, session, int(scan), nifit_file_name)


def get_scan_sets(input_dir):
    scans = {}
    dcm_base_folder = input_dir + os.path.sep + 'SCANS'
    if os.path.exists(dcm_base_folder):
        for scan_dir in os.listdir(dcm_base_folder):
            if os.path.isdir(dcm_base_folder + os.path.sep + scan_dir):
                scan = os.path.basename(scan_dir)
                dcm = glob(dcm_base_folder + os.path.sep + scan_dir + os.path.sep + 'DICOM' + os.path.sep + '*.dcm')
                scans[scan] = dcm
    else:
        print(dcm_base_folder + ' does not exist.')
    return scans


def dcm_to_nii(dcm, nii_file_name):
    try:
        stacks = dcmstack.parse_and_stack(dcm)
        for stack in stacks.itervalues():
            nii = stack.to_nifti()
            nii.to_filename(nii_file_name)
            break
    except:
        print 'dcmstack DICOM to NIFTI failed.'


def get_nifti_resource_id(json):
    result_set = json['ResultSet']
    if result_set is None:
        return

    result = result_set['Result']
    if result is None:
        return

    try:
        for resource in result:
            if resource['format'] != "NIFTI":
                continue
            return int(resource['xnat_abstractresource_id'])
    except TypeError:
        return

    return


def post_nifti(server, user, password, experiment, scan, file_name):
    base_url = '%(server)s/data/experiments/%(experiment)s/scans/%(scan)d/resources' % {"server": server,
                                                                                        "experiment": experiment,
                                                                                        "scan": scan}
    put_url = '%(base_url)s/NIFTI?format=NIFTI'
    post_url = '%(base_url)s/%(resource_id)d/files/%(resource_name)s?file_upload=true&format=NIFTI'
    resource_template = '%(experiment)s.%(scan)03d.nii.gz'
    session = requests.session()

    # Create resource folder
    # PUT https://central.xnat.org/REST/experiments/CENTRAL_E07096/scans/2/resources/NIFTI?format=NIFTI
    put_instance = put_url % {"base_url": base_url}
    put_response = session.put(put_instance, auth=(user, password))
    print 'Create: %d' % put_response.status_code

    # Get new folder resource ID
    # GET https://central.xnat.org/REST/experiments/CENTRAL_E07096/scans/2/resources
    get_response = session.get(base_url)
    print 'Get: %d' % get_response.status_code
    resource_id = get_nifti_resource_id(get_response.json())

    if resource_id is None:
        print "Couldn't find valid resource ID, quitting..."
        exit()

    # POST https://central.xnat.org/REST/experiments/CENTRAL_E07096/scans/2/resources/123232250/files/CENTRAL_E07096.002.nii
    # .gz?file_upload=true&format=NIFTI
    resource_name = resource_template % {"experiment": experiment, "scan": scan}
    post_instance = post_url % {"base_url": base_url, "resource_id": resource_id, "resource_name": resource_name}
    files = {'file': open(file_name, 'rb')}
    post_response = session.post(post_instance, files=files)
    print 'File: %d' % post_response.status_code



if __name__ == "__main__":
    main(sys.argv[1:])
