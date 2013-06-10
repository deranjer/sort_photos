#!/usr/bin/python

import os
import sys
import shutil
import datetime
import EXIF
import string
import re
import dateutil.parser as dateParser

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

#sort only these file ext.  Comment this line out to sort ALL file types
exts = ['.jpeg', '.jpg', '.exif', '.tiff', '.raw', '.gif', '.bmp', '.png', '.pam', '.webp', '.svg', '.rgbe']

#exclude dirs here (if folder contains tree structure) that you don't want moved/sorted
excludes = ['test test',  'atest']

#If you want to move pictures with NO/BROKEN metadata to the ROOT folder of your new dir/sort dir, set true here
#else pictures will stay where they were
move_no_meta = True

#Will use datetime to guess what year/day the picture belongs in
guess_date_from_name=True

#clamp year range.  If dateutil guesses a crazy year (way old or way past current, this will clamp it to between these years
yearRangeOld = 1960
yearRangeNew = 2013

#Adding full dir structure.. could search each list element.. but kinda risky
excludes = [odir + "/" + s for s in excludes]

dry_run=False


#Functions are here
def reduceString(string):
    while len(string) > 4:
        print(string)
        string = string[:-1]
        return string
    else:
        year=''
        month=''
        day=''
        return(year, month, day)

def guessDate(file, fileName):
    while fileName:
        #purge all char from filename
        try:
            fileName = fileName.translate(None, string.letters)
        except AttributeError:
            print("Whoops, error purging all chars from filename.... passing")
            pass
        try:
            #remove leading underscore, or any %, or () if there
            fileName = re.sub(r"(\(|\)|\b_|%)", r"", fileName)
        except TypeError:
            print("Filename error... passing")
            pass
        print("Guesssing date from ", fileName)
        try:
            dateString = dateParser.parse(fileName, fuzzy=False)
            print("Guessed date", dateString)
            year=dateString.year
            month = dateString.month
            day=dateString.day
            #in case dateParser starts giving the current date for unknowns, but I THINK fuzzy must be set to True for thats
            now = datetime.datetime.now()
            currentday = now.day
            currentmonth = now.month
            currentyear = now.year
            if currentday == day and currentmonth == month and currentyear == year:
                print("Date same as today.. invalid")
                year = "0000"
            if (year > yearRangeNew) or (year < yearRangeOld):
                print("Year out of acceptable range... invalid")
                year = "0000"
            return(str(year),str(month),str(day))
        except ValueError:
            print("No guess for ", fileName)
        except OverflowError:
            pass
        except AttributeError:
            print("Incorrect object, perhaps tuple?  Manually forcing a no metadata call")
            day = ''
            month = ''
            year = "0000"
            return year,month,day
        fileName = reduceString(fileName)
    #if we get no metadata
    day = ''
    month = ''
    year = "0000"
    return year,month,day


def guessMetaData(fullfname, file):
    print "No metadata for ",  fullfname
    if (move_no_meta == True) and (guess_date_from_name == True): #going to now guess at the date
            fileName = os.path.splitext(file)[0]
            year,month,day = guessDate(file, fileName)
            if year is "0000":
                print("Unacceptable metadata, moving to root")
                sortFile(fullfname, file, month='', day='', year='', metaData=True)
            else:
                sortFile(fullfname, file, str(month), str(day), str(year), metaData=True)
    else:
        if (move_no_meta == True) and (guess_date_from_name == False):
            f.close()
            sortFile(fullfname, file, month='', day='', year='', metaData=False)


def sortFile(fullfname, file, month, day, year, metaData): #have the metadata true/false tag to save processing
    if dry_run==False:
        if metaData == True: #If we have true metadata
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
    

        else: #If our metadata is false
            if move_dir == True:
                newfullfname = ndir+"/"+file
            else:
                newfullfname=odir+"/"+file
            print fullfname+" moving to "+newfullfname
            if dry_run==False:
                shutil.move (fullfname, newfullfname)
    

#start of main program loop
for dir, subdir, files in os.walk(odir):
    if dir in excludes: #TODO, fix, not working
        print "Skipping dir", dir
    subdir[:] = [dn for dn in subdir if os.path.join(dir, dn) not in excludes ]    #google code, no clue how this works
    print "Searching dir",  dir
    for file in files:
        if "exts" in vars(): #if variable is defined.
            fileExt = os.path.splitext(file)[1]
            fileExt = fileExt.lower() #making it lowercase to match the excludes ext library
            if fileExt not in exts: 
                print("Excluding file: ", file)
                continue
        try:
            fullfname=dir+"/"+file
            f = open(fullfname, 'rb')

            tags = EXIF.process_file(f, details=False)
            if len(tags)>0:
                print "Found metadata for ",  fullfname
                if 'EXIF DateTimeOriginal' in tags:
                    dtt=tags['EXIF DateTimeOriginal'].values
                    year=dtt[0:4]
                    month = dtt[5:7]
                    day=dtt[8:10]
                else: #nulling out the values if they are not found in the EXIF data to stop error #todo (try except)
                    year = ''
                    day = ''
                    month = ''
                f.close()
            #If EXIF null or zero'd, move to new dir root (if set in options)
                if (year or day or month == '') or (year or day or month == "0000"):
                    print "Incorrect metadata for ",  fullfname
                    guessMetaData(fullfname, file)
                else: #we have (assumed) correct metadata
                    month=datetime.date(int(year), int(month), int(day)).strftime('%B') #extracting month/day/year
                    sortFile(fullfname, file, month, day, year, metaData=True)

            else:
                guessMetaData(fullfname, file) #no metadata found, so going to start guessing
                
                    
        except IOError:
            print "%s: Cannot open file for read-write." % fullfname
