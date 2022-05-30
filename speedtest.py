#!/usr/bin/env /mnt/DroboFS/Shares/DroboApps/python2/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1'

import argparse
import glob
import re
import math
import os
import datetime


# Set the file content result's string pattern
download_pattern = r'(?:Download:.+?)([0-9]?[0-9]+.+[0-9]+[0-9]+)'
upload_pattern = r'(?:Upload:.+?)([0-9]?[0-9]+.+[0-9]+[0-9]+)'


# Command parameters parsing and treatment
parser = argparse.ArgumentParser()
parser.add_argument(
  '-c','--cut',
  help='Adjust the correction factor removing N extreme values',
  default=0,
  type=int)
parser.add_argument(
  '-d','--directory',
  help='The directory where the test files are stored',
  default='.',
  type=str)
parser.add_argument(
  '-e','--extension',
  help='Extension of the test files other than .log (default)',
  default=0,
  type=str)
parser.add_argument(
  '-f','--csv',
  action='store_true',
  help='Extract all data as a CSV file')
parser.add_argument(
  '-p','--printall',  
  action='store_true',
  help='Print all individual results before the final mean/median result'),
args = parser.parse_args()

cut = args.cut if args.cut else 0
directory_pattern = r'(^\/?.+)(?:\/$)?'
directory = re.search(directory_pattern, args.directory).group(0) if args.directory and re.search(directory_pattern, args.directory) else '.'
extension_pattern = r'(?:^\.)?(.+)'
extension = re.search(extension_pattern, args.extension).group(1) if args.extension and re.search(extension_pattern, args.extension) else 'log'

print directory

def creation_date(filename):
  time = os.path.getctime(filename)
  return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M')


# Read all the designated files in the current directory or desired path
path = directory + '/*.' + extension
files = glob.glob(path)

def check_speed():
  downloads = []
  uploads = []
  csv = {}

  if len(files) == 0:
    print '  No speedtest result files found!'

  else:
    print '  Iterating in {0} .{1} files at path "{2}" ...'.format(len(files), extension, directory)
   
    for file in files:
      created = creation_date(file)

      with open(file) as log:
        content = log.read()

        speeds = [] 

        download_match = re.search(download_pattern, content)
        if download_match:
          d = round(float(download_match.group(1)),2)
          downloads.append(d)
          speeds.append(str(d).format('%2.f'))

        upload_match = re.search(upload_pattern, content)
        if upload_match:
          u = round(float(upload_match.group(1)),2)
          uploads.append(u)
          speeds.append(str(u).format('%2.f'))

      csv[created] = speeds

    if args.csv:
      with open('Exported-{0}.csv'.format(datetime.datetime.today().strftime('%Y-%m-%d-%H-%M')), 'w') as f:
        f.write('Date;Download;Upload\n')

        for date, speeds in csv.iteritems():
          if speeds:
            f.write('{0};{1};{2}\n'.format(date, speeds[0], speeds[1]))


    # Sort the values cutting the deviation
    sorted_download = sorted(downloads)[cut:-cut] if cut > 0 else sorted(downloads)
    sorted_upload = sorted(uploads)[cut:-cut] if cut > 0 else sorted(uploads) 

    # and count them
    count_download = len(sorted_download)
    count_upload = len(sorted_upload)

    # Sum all download speeds
    total_download = math.fsum(sorted_download)
    total_upload = math.fsum(sorted_upload)

    if args.printall: print '  Downloads: ' + ', '.join(map(str, downloads))
    if count_download > 0: print '  Mean/Median Download Speed ({0} tests): {1} MBit/s'.format(count_download, round(total_download / count_download,2))
    if args.printall: print '  Uploads: ' + ', '.join(map(str, uploads))
    if count_upload > 0: print '  Mean/Median Upload Speed: ({0} tests): {1} MBit/s'.format(count_upload, round(total_upload / count_upload,2))

try:
  check_speed()
except KeyboardInterrupt:
  print '\nCancelling...'
