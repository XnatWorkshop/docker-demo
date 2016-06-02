# /bin/env python

# Converts a directory of one or more DICOM files into the NIfTI format
# Primary use is to test the XNAT Docker service.
# Input directory is assumed to be /input
#   Input directory format is assumed to be /input/SCANS/{scan_id}/DICOM/
# Output directory is assumed to be /output
#   Output directory format will be generated as /output/SCANS/{scan_id}/NIFTI/


# USAGE: python pyscript.py 

import sys
import os
import dcmstack
import getopt
from glob import glob


def main(argv):

    input_dir = '/input'
    output_dir = '/output'

    # parse input directory structure by scan id
    for scan, dcm in get_scan_sets(input_dir).iteritems():
        # use dcmstack to create a nifti file from each scan set
        nifti_file_name = os.path.join(output_dir, scan + '.nii.gz');
        dcm_to_nii(dcm, nifti_file_name)


def get_scan_sets(input_dir):
    scans = {}
    dcm_base_folder = os.path.join(input_dir, 'SCANS')
    if os.path.exists(dcm_base_folder):
        for scan_dir in os.listdir(dcm_base_folder):
            if os.path.isdir(os.path.join(dcm_base_folder, scan_dir)):
                scan = os.path.basename(scan_dir)
                dcm = glob(os.path.join(dcm_base_folder, scan_dir, 'DICOM', '*.dcm'))
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


if __name__ == "__main__":
    main(sys.argv[1:])

