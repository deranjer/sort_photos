#!/usr/bin/python

import os
import sys
import shutil
import datetime
import EXIF

# This is a simple script just for sorting photos (based on EXIF data) in current folder into folders like 
# C:\Users\Administrator\Arx\date\<year>\<month>\<day>\*.jpg
# <month> is in full english form (January, Feburary, etc)

# Python 2.x

# -- dennis(a)yurichev.com

odir='C:\\Users\\Administrator\\Arx\\date\\'

dry_run=False

for dir, subdir, files in os.walk(os.getcwd()):
   for file in files:
      try:
         fullfname=dir+"/"+file
         f = open(fullfname, 'rb')

         tags = EXIF.process_file(f, details=False)
         if len(tags)>0:
            if 'EXIF DateTimeOriginal' in tags:
               dtt=tags['EXIF DateTimeOriginal'].values
            year=dtt[0:4]
            day=dtt[8:10]
            month=datetime.date(int(year), int(dtt[5:7]), int(day)).strftime('%B')

            f.close()

            if dry_run==False:
                if os.path.isdir (odir+"\\"+year)==False:
                   os.mkdir (odir+"\\"+year)
                if os.path.isdir (odir+"\\"+year+"\\"+month)==False:
                   os.mkdir (odir+"\\"+year+"\\"+month)
                if os.path.isdir (odir+"\\"+year+"\\"+month+"\\"+day)==False:
                   os.mkdir (odir+"\\"+year+"\\"+month+"\\"+day)
            newfullfname=odir+"\\"+year+"\\"+month+"\\"+day+"\\"+file
            print fullfname+" moving to "+newfullfname
            if dry_run==False:
                shutil.move (fullfname, newfullfname)

      except IOError:
         print "%s: Cannot open file for read-write." % fullfname
