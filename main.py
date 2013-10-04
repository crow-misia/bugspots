#!/bin/python
# -*- coding: utf-8 -*-

import sys, os
import math
import datetime
import subprocess
import csv
import optparse

def str2time(v):
    return datetime.datetime.strptime(v, "%Y-%m-%d")
    
def daydifference(after, before):
    return (before - after).days

def getdates(lines):
    datelist = []
    for line in lines:
        h = line.find("Date:")
        if h != -1:
            date = str2time(line[8:18]).date()
            datelist.append(date)
    return datelist

def get_gitlog(options, after, path):
    command = "git"

    text = subprocess.check_output(["git", "log", "--after=\""+after.strftime("%Y-%m-%d")+"\"", "--no-decorate", "--date=short", path], stderr=subprocess.STDOUT, shell=True)
    lines = text.split("\n")

    return lines

def google_score(duration, existing):
    ti = 0
    if (existing != 0):
        ti = duration * 1.0 / existing
    return 1.0 / (1.0 + math.exp((-12.0 * ti) + 12.0))

def calc_fix_score(datelist):
    if len(datelist) < 1:
        return 0
    first_commit_date= datelist[len(datelist)-1]
    existing_days = daydifference(first_commit_date, datetime.date.today())
    score = 0
    for date in datelist:
        duration = daydifference(first_commit_date, date)
        score += google_score(duration, existing_days)
    return score

def calc_score(options, after, path):
    lines = get_gitlog(options, after, path)
    datelist = getdates(lines)
    score = calc_fix_score(datelist)
    return score

def get_pathes(root):
    filelist = []
    for root, dirs, files in os.walk(root):
        for name in files:
            if not name.endswith("\\") and \
               not name.endswith(".png") and \
               not name.endswith(".jpg") and \
               not name.endswith(".jpeg") and \
               not name.endswith(".gif"):
                filelist.append(os.path.join(root, name))

        if '.git' in dirs:
            dirs.remove('.git')
        if '.metadata' in dirs:
            dirs.remove('.metadata')
    return filelist

def perse_option():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--days", dest="days",
        default=30,
        help="Days ago to compute bug factor")

    (options, args) = parser.parse_args()

    if len(args) >= 1:
        target = args[0]
    else:
        target = "."

    return (options, target)


os.putenv("TERM", "msys")

(options, target) = perse_option()

outputfile = "bugspots_score.csv"

print 'target  :', target
print 'days    :', options.days
print 'output  :', outputfile

after = datetime.datetime.today() - datetime.timedelta(days=options.days)

writercsv = csv.writer(file(outputfile,"wb"))

filelist = get_pathes(target)
for f in filelist:
    score = calc_score(options, after, f)
    if score > 0:
        writercsv.writerow([f, score])
