# /bin/env python

# Converts a directory of one or more DICOM files into the NIfTI format
# Primary use is to test the XNAT Docker service.
# Input directory is assumed to be /input
#   Input directory format is assumed to be /data/input/*.dcm
# Output directory is assumed to be /data/output
#   Output directory format will be generated as /data/output/data.nii.gz

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
        nifit_file_name = output_dir + os.path.sep + 'scan' + '.nii.gz';
        dcm_to_nii(dcm, nifit_file_name)


def get_scan_sets(input_dir):
    dcm_base_folder = input_dir
    if os.path.exists(dcm_base_folder):
        dcm = glob(dcm_base_folder + os.path.sep + '*.dcm')
        scan = dcm
    else:
        print(dcm_base_folder + ' does not exist.')
    return scan


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
