#!/usr/bin/env python
#coding: utf-8

import datetime
import glob
import itertools
import os
import re
import sqlite3
import stat
import subprocess
import time
import urllib2

HOME_DIRECTORY = os.environ['HOME']
PROJECT_FILES = (".progject", "Makefile")


def is_dot_file(f):
    return f.startswith(".")


def safe_stat(p):
    try:
        return os.stat(p)
    except:
        return None


def get_filesystem_history(target_dirs):
    result = []
    timeFields = (stat.ST_MTIME, stat.ST_CTIME)
    accumulateTargetStack = []
    for root, dirs, files in itertools.chain(*map(os.walk, target_dirs)):
        accumulateTagetForTheDir = (root, [])
        accumulateTargetStackPushed = False
        for f in files:
            if f in PROJECT_FILES:
                projectPath = os.path.join(root, f)
                accumulateTargetStack.append((projectPath, []))
                accumulateTargetStackPushed = True
                break # for f
        try:
            t = accumulateTagetForTheDir if not accumulateTargetStack else accumulateTargetStack[-1]
            s = safe_stat(root)
            if s:
                t[1].extend(s[field] for field in timeFields)
            for f in files:
                p = os.path.join(root, f)
                s = safe_stat(p)
                if s:
                    t[1].extend(s[field] for field in timeFields)
            if t is accumulateTagetForTheDir and t[1]:
                result.append((max(t[1]), t[0].decode('utf-8')))
        finally:
            if accumulateTargetStackPushed:
                t = accumulateTargetStack.pop()
                if t[1]:
                    result.append((max(t[1]), t[0].decode('utf-8')))
        dirs[:] = [d for d in dirs if not is_dot_file(d)]
    return result


def get_trash_history():
    result = []
    pat = re.compile(r"^(\d+)-(\d+)-(\d+)[ \t]+(\d+):(\d+):(\d+)[ \t]+(.*)")
    output = subprocess.check_output(["list-trash"])
    for L in output.decode('utf-8').split('\n'):
        m = pat.match(L)
        if m:
            a = time.mktime(datetime.datetime(*[int(m.group(i)) for i in range(1, 6 + 1)]).timetuple())
            path = m.group(7)
            result.append((a, path))
    return result


def extract_from_db_it(db_file, query, row_pred=None):
    if not row_pred:
        row_pred = lambda row: True
    con = sqlite3.connect(db_file)
    try:
        for row in con.execute(query):
            if row_pred(row):
                yield row
    finally:
        con.close()


def get_keyvalue_in_url(key, url):
    url = url.replace("?", "&")
    k = key + "="
    return [field for field in url.split("&") if field.startswith(k)]


def normalize_url(url):
    try:
        url = urllib2.unquote(url.encode('utf-8')).decode('utf-8')
    except UnicodeDecodeError:
        pass

    if url.endswith("/"):
        url = url[:-1]
    
    # google search
    m = re.match("^https?://www.google.[^/]+/search[?].*", url)
    if m:
        r = get_keyvalue_in_url("q", url)
        if not r:
            return url
        return u" ".join(r)
    
    # google search result's links
    m = re.match("^https?://www.google.[^/]+/url[?].*", url)
    if m:
        r = get_keyvalue_in_url("url", url)
        if not r:
            return url
        return u" ".join(r)

    # youtube
    m = re.match("^https?://www.youtube.com/watch[?].*", url)
    if m:
        r = get_keyvalue_in_url("v", url)
        if not r:
            return url
        return u" ".join(r)
    
    # others
    return url


def get_firefox_history():
    dbFileCandidates = glob.glob(os.path.join(HOME_DIRECTORY, 
            ".mozilla/firefox/*.default/places.sqlite"))
    query = u"select last_visit_date, url from moz_places"
    def is_valid_row(row):
        return row[0] is not None
    timeUrlList = []
    for f in dbFileCandidates:
        for a, url in extract_from_db_it(f, query, is_valid_row):
            u = normalize_url(url)
            timeUrlList.append((a // 1000000, u))
    return timeUrlList


def get_chromium_history():
    dbFile = os.path.join(HOME_DIRECTORY, ".config/chromium/Default/History")
    query = u"select last_visit_time, url from urls"
    timeUrlList = []
    for a, url in extract_from_db_it(dbFile, query):
        u = normalize_url(url)
        timeUrlList.append((a, u))
    return timeUrlList


USAGE = u"""
Usage: mondaymoring [OPTIONS] <directory>...
  Searches recent working items: the files that you were editing, the urls you were browsing.
Opition
  -d <num>: duaration. searches histories in num days (3). '-' for infinite.
  -C: no Chromium history.
  -F: no Firefox history.
  -H: no home directory's history.
  -T: no Gnome Trash history.
  --version: shows version.
"""[1:-1]

VERSION = (0, 1, 0)


def format_time(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def main():
    import sys
    import codecs
    import getopt
    
    writefunc = codecs.getwriter('utf-8')(sys.stdout).write
    logfunc = codecs.getwriter('utf-8')(sys.stderr).write
    
    optionChromium = True
    optionFirefox = True
    optionTrash = True
    duaration = 3
    targetDirs = ['~']
    
    opts, args = getopt.gnu_getopt(sys.argv[1:], "d:hCFHT", ["help", "version"])
    for k, v in opts:
        if k in ("-h", "--help"):
            writefunc(USAGE + u"\n")
            return
        elif k == "--version":
            writefunc(u"mondaymorning %d.%d.%d" % VERSION)
            return
        elif k == "-d":
            if v == "-":
                duaration = 0
            duaration = int(v)
        elif k == "C":
            optionChromium = False
        elif k == "F":
            optionFirefox = False
        elif k == "T":
            optionTrash = False
        elif k == "H":
            targetDirs = [d for d in targetDirs if d != "~"]
        else:
            assert False
    targetDirs.extend(args)

    targetDirs = [(HOME_DIRECTORY if d == "~" else d) for d in targetDirs]
    
    items = []

    def unique_urls(tus):
        uniqs = []
        for k, g in itertools.groupby(sorted(tus, key=lambda t_u: t_u[1])):
            uniqs.append(g.next())
        return uniqs
    
    tus = get_filesystem_history(targetDirs)
    uniqueTus = unique_urls(tus)
    items.extend((t, "file", u) for t, u in uniqueTus)

    if optionTrash:
        try:
            tus = get_trash_history()
            uniqueTus = unique_urls(tus)
            items.extend((t, "trash", u) for t, u in uniqueTus)
        except OSError as e:
            logfunc("failure in extracting Trash history: %s\n" % repr(e))
            logfunc("> (trash-cli has not been installed yet?)\n")

    if optionFirefox:
        try:
            tus = get_firefox_history()
            uniqueTus = unique_urls(tus)
            items.extend((t, "web", u) for t, u in uniqueTus)
        except sqlite3.OperationalError as e:
            logfunc("failure in extracting Firefox history: %s\n" % repr(e))

    if optionChromium:
        try:
            tus = get_chromium_history()
            tus = get_firefox_history()
            uniqueTus = unique_urls(tus)
            items.extend((t, "web", u) for t, u in uniqueTus)
        except sqlite3.OperationalError as e:
            logfunc("failure in extracting Chromium history: %s\n" % repr(e))
            logfunc("> (Chromium is running? Close Chromium before invoke mondaymorning)\n")
    
    items.sort(reverse=True)
    if duaration and items:
        latestTime = items[0][0]
        startingTime = latestTime - duaration * 24 * 60 * 60
        for i, item in enumerate(items):
            if item[0] <= startingTime:
                items[:] = items[:i]
                break # for i
    
    lastKU = None
    for t, k, u in items:
        ku = (k, u)
        if ku != lastKU:
            writefunc(u"%s %s %s\n" % (format_time(t), k, u))
            lastKU = ku


if __name__ == '__main__':
    main()
