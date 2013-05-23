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

#set dir for original pictures
odir='/mnt/media/Pictures'
#If you want to file pictures in a new directory, specify here, make sure dir exits
move_dir=True
ndir='/mnt/media/NewPictures2'
#If you want to move pictures with NO/BROKEN metadata to the ROOT folder of your new dir/sort dir, set true here
#else pictures will stay where they were
move_no_meta = True
#exclude dirs here (if folder contains tree structure) that you don't want moved/sorted
excludes = ['test test',  'atest']
#Adding full dir structure.. could search each list element.. but kinda risky
excludes = [odir + "/" + s for s in excludes]


dry_run=False

for dir, subdir, files in os.walk(odir):
    print "Searching dir",  dir
    if dir in excludes:
        print "Excluding directory ",  dir
        pass
    for file in files:
        try:
            fullfname=dir+"/"+file
            f = open(fullfname, 'rb')

            tags = EXIF.process_file(f, details=False)
            if len(tags)>0:
                print "Found metadata"
                if 'EXIF DateTimeOriginal' in tags:
                    dtt=tags['EXIF DateTimeOriginal'].values
                    year=dtt[0:4]
                    month = dtt[5:7]
                    day=dtt[8:10]
                else: #nulling out the values if they are not found in the EXIF data to stop error
                    year = ''
                    day = ''
                    month = ''
                f.close()
               #If EXIF null or zero'd, move to new dir root (if set in options)
                if (year or day or month == '') or (year or day or month == "0000"):
                    print "Incorrect metadata"
                    if move_no_meta == True:
                        if move_dir == True:
                            newfullfname = ndir+"/"+file
                        else:
                            newfullfname=odir+"/"+file
                        print fullfname+" moving to "+newfullfname
                        if dry_run==False:
                            shutil.move (fullfname, newfullfname)
                else:
                    month=datetime.date(int(year), int(month), int(day)).strftime('%B')

                    if dry_run==False:
                        if move_dir == True:
                            print "Moving to new dir..."
                            if os.path.isdir (ndir+"/"+year)==False:
                                 os.mkdir (ndir+"/"+year)
                            if os.path.isdir (ndir+"/"+year+"/"+month)==False:
                                os.mkdir (ndir+"/"+year+"/"+month)
                            if os.path.isdir (ndir+"/"+year+"/"+month+"/"+day)==False:
                                os.mkdir (ndir+"/"+year+"/"+month+"/"+day)
                            newfullfname=ndir+"/"+year+"/"+month+"/"+day+"/"+file
                    else:
                        print "Organizing in same dir..."
                        if os.path.isdir (odir+"/"+year)==False:
                            os.mkdir (odir+"/"+year)
                        if os.path.isdir (odir+"/"+year+"/"+month)==False:
                            os.mkdir (odir+"/"+year+"/"+month)
                        if os.path.isdir (odir+"/"+year+"/"+month+"/"+day)==False:
                            os.mkdir (odir+"/"+year+"/"+month+"/"+day)
                        newfullfname=odir+"/"+year+"/"+month+"/"+day+"/"+file
                    print fullfname+" moving to "+newfullfname
                    if dry_run==False:
                        shutil.move (fullfname, newfullfname)
            else:
                f.close()
                print "No metadata!"
                if move_no_meta == True:
                    if move_dir == True:
                        newfullfname = ndir+"/"+file
                    else:
                        newfullfname=odir+"/"+file
                    print fullfname+" moving to "+newfullfname
                    if dry_run==False:
                        shutil.move (fullfname, newfullfname)
                else:
                    pass
        except IOError:
            print "%s: Cannot open file for read-write." % fullfname
