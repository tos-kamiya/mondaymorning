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

HOME_DIRECTORY = u"" + os.environ['HOME']
PROJECT_FILES = (
     u".progject", # Eclipse project 
     u"Makefile", # makefile
     u"build.xml", # Ant
)


def is_dot_file(f):
    return f not in (".", "..") and f.startswith(u".")


def safe_stat_time(p):
    try:
        s = os.stat(p)
    except:
        return 0
    return max(s[stat.ST_MTIME], s[stat.ST_CTIME])


def merge_paths_by_directory_structure(L):
    tdfs = []
    lastA, lastD = None, None
    for a, p in L:
        d, f = os.path.split(p)
        if not d:
            d, f = p, u""  # warning: "." is split into ("", "."), instead of (".", "")
        if a != lastA or p != lastD:
            tdfs.append((a, d, f))
        lastA, lastD = a, d
    mergedPaths = []
    for k, g in itertools.groupby(tdfs, lambda adf: adf[:2]):
        items = list(g)
        d = k[1]
        if d != u'/':
            d = d + u'/'
        if len(items) == 1:
            f = items[0][2]
            mergedPaths.append((k[0], d + f))
        else:
            fs = u"{%s}" % u",".join(item[2] for item in items)
            mergedPaths.append((k[0], d + fs))
    return mergedPaths


def normalize_filepath(path):
    if path.startswith(HOME_DIRECTORY + "/"):
        return u"~" + path[len(HOME_DIRECTORY):]
    return path


def listdir(directory):
    try:    
        files = os.listdir(directory)
    except OSError:
        return None
    files = [f for f in files if f not in (".", "..")]
    fileFnames, dirFnames = [], []
    for f in files:
        p = os.path.join(directory, f)
        if os.path.isfile(p):
            fileFnames.append(f)
        elif os.path.islink(p):
            pass
        elif os.path.isdir(p):
            dirFnames.append(f)
    return fileFnames, dirFnames


def get_filesystem_history(target_dirs, truncate_time=None):
    doneDirSet = set()
    timestampTable = {}
        
    def max_timestamp(directory, target):
        if directory in doneDirSet:
            return
        doneDirSet.add(directory)
        r = listdir(directory)
        if r is None:
            return
        fileFnames, dirFnames = r
        for f in fileFnames:
            if f in PROJECT_FILES:
                target = directory + "*"
                break # for f
        curTarget = target if target else directory
        for f in fileFnames:
            p = os.path.join(directory, f)
            t = safe_stat_time(p)
            if t:
                t = t if truncate_time is None else truncate_time(t)
                mt = timestampTable.get(curTarget, 0)
                timestampTable[curTarget] = max(mt, t)
        for f in dirFnames:
            if not is_dot_file(f):
                p = os.path.join(directory, f)
                t = safe_stat_time(p)
                if t:
                    t = t if truncate_time is None else truncate_time(t)
                    mt = timestampTable.get(curTarget, 0)
                    timestampTable[curTarget] = max(mt, t)
                    max_timestamp(p, target)
    
    for d in target_dirs:
        max_timestamp(d.decode('utf-8'), None)
    
    result = [(mt, normalize_filepath(p)) for p, mt in timestampTable.iteritems()]
    result.sort(reverse=True)
    result = merge_paths_by_directory_structure(result)
    return result


def get_trash_history(truncate_time=None):
    result = []
    pat = re.compile(ur"^(\d+)-(\d+)-(\d+)[ \t]+(\d+):(\d+):(\d+)[ \t]+(.*)")
    output = subprocess.check_output(["list-trash"])
    for L in output.decode('utf-8').split('\n'):
        m = pat.match(L)
        if m:
            t = time.mktime(datetime.datetime(*[int(m.group(i)) for i in range(1, 6 + 1)]).timetuple())
            t = t if truncate_time is None else truncate_time(t)
            path = m.group(7)
            result.append((t, path))
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
    m = re.match("^https?://(.*)", url)
    if m:
        url = m.group(1)
    
    # google search
    m = re.match("^(www[.]google[.][^/]+/search[?]).*", url) or \
            re.match("^(www[.]google[.][^/]+/#).*", url) or \
            re.match("^(scholar[.]google[.][^/]+/scholar[?]).*", url)
    if m:
        r = get_keyvalue_in_url("q", url)
        if r:
            return m.group(1) + u"&".join(r)
        else:
            return url
    
    # google search result's links
    if re.match("^www[.]google[.][^/]+/url[?].*", url):
        r = get_keyvalue_in_url("url", url)
        if r:
            if len(r) == 1:
                return r[0][4:] # drop "url="
            return u" ".join(r)
        else:
            return url

    # youtube
    if re.match("^www[.]youtube[.]com/watch[?].*", url):
        r = get_keyvalue_in_url("v", url)
        if r:
            return u"www.youtube.com/watch?" + u"&".join(r)
        else:
            return url

    # youtube search
    if re.match("^www[.]youtube[.]com/results[?]search_query=", url):
        r = get_keyvalue_in_url("search_query", url)
        if r:
            return u"www.youtube.com/results?" + u"&".join(r)
        else:
            return url
    
    # twitter
    if re.match("^twitter[.]com", url):
        r = get_keyvalue_in_url("original_referer", url)
        if r:
            return u" ".join(r)
        else:
            m = re.match("^twitter[.]com/#!/(.*)", url)
            if m:
                return u"twitter.com/" + m.group(1)
        return url
        
    # others
    return url


def merge_url_by_last_param(L):
    tdfs = []
    for t, url in L:
        i = url.rfind('&')
        if i >= 0:
            d, f = url[:i + 1], url[i + 1:]
            tdfs.append((t, d, f))
        else:
            d, f = url, ''
            tdfs.append((t, d, f))
    mergedUrls = []
    for k, g in itertools.groupby(tdfs, lambda adf: adf[:2]):
        items = list(g)
        d = k[1]
        if len(items) == 1:
            f = items[0][2]
            mergedUrls.append((k[0], d + f))
        else:
            fs = u"{%s}" % u",".join(item[2] for item in items)
            mergedUrls.append((k[0], d + fs))
    return mergedUrls


def get_firefox_history(truncate_time=None):
    dbFileCandidates = glob.glob(os.path.join(HOME_DIRECTORY, 
            ".mozilla/firefox/*.default/places.sqlite"))
    query = u"select last_visit_date, url from moz_places"
    def is_valid_row(row):
        return row[0] is not None
    timeUrlList = []
    for f in dbFileCandidates:
        for t, url in extract_from_db_it(f, query, is_valid_row):
            u = normalize_url(url)
            t = t // 1000000
            t = t if truncate_time is None else truncate_time(t)
            timeUrlList.append((t, u))
    return timeUrlList


def get_chromium_history(truncate_time=None):
    dbFile = os.path.join(HOME_DIRECTORY, ".config/chromium/Default/History")
    query = u"select last_visit_time, url from urls"
    timeUrlList = []
    for t, url in extract_from_db_it(dbFile, query):
        u = normalize_url(url)
        t = t // 10000000
        t = t if truncate_time is None else truncate_time(t)
        timeUrlList.append((t, u))
    return timeUrlList


USAGE = u"""
Usage: mondaymoring [OPTIONS] <directory>...
  Searches recent working items: the files that you were editing, the urls you were browsing.
Opition
  -d <num>: duaration. searches histories in num days (3). '-' for infinite.
  -s: uses second as time resolution, instead of minute.
  -C: no Chromium history.
  -F: no Firefox history.
  -H: no home directory's history.
  -T: no Gnome Trash history.
  -W: same as -C -F.
  --version: shows version.
"""[1:-1]

VERSION = (0, 2, 0)


def main():
    import sys
    import codecs
    import getopt
    
    writefunc = codecs.getwriter('utf-8')(sys.stdout).write
    logfunc = codecs.getwriter('utf-8')(sys.stderr).write
    
    optionChromium = True
    optionFirefox = True
    optionTrash = True
    timeResolution = 'min'
    duaration = 3
    targetDirs = ['~']
    
    opts, args = getopt.gnu_getopt(sys.argv[1:], "d:hsCFHTW", ["help", "version"])
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
            else:
                duaration = int(v)
        elif k == "-C":
            optionChromium = False
        elif k == "-F":
            optionFirefox = False
        elif k == "-T":
            optionTrash = False
        elif k == "-H":
            targetDirs = [d for d in targetDirs if d != "~"]
        elif k == "-W":
            optionChromium = False
            optionFirefox = False
        elif k == "-s":
            timeResolution = 'sec'
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
    
    if timeResolution == 'min':
        def truncate_time(t):
            return t - time.localtime(t).tm_sec
        def format_time(t):
            return time.strftime("%Y-%m-%d %H:%M", time.localtime(t))
    else:
        truncate_time = None
        def format_time(t):
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        
    tus = get_filesystem_history(targetDirs, truncate_time=truncate_time)
    uniqueTus = unique_urls(tus)
    items.extend((t, "file", u) for t, u in uniqueTus)

    if optionTrash:
        try:
            tus = get_trash_history(truncate_time=truncate_time)
            uniqueTus = unique_urls(tus)
            items.extend((t, "trash", u) for t, u in uniqueTus)
        except OSError as e:
            logfunc("failure in extracting Trash history: %s\n" % repr(e))
            logfunc("> (trash-cli has not been installed yet?)\n")

    tus = []
    if optionFirefox:
        try:
            tus.extend(get_firefox_history(truncate_time=truncate_time))
        except sqlite3.OperationalError as e:
            logfunc("failure in extracting Firefox history: %s\n" % repr(e))

    if optionChromium:
        try:
            tus.extend(get_chromium_history(truncate_time=truncate_time))
        except sqlite3.OperationalError as e:
            logfunc("failure in extracting Chromium history: %s\n" % repr(e))
            logfunc("> (Chromium is running? Close Chromium before invoke mondaymorning)\n")

    uniqueTus = unique_urls(tus)
    mergedTus = merge_url_by_last_param(sorted(uniqueTus))
    items.extend((t, "web", u) for t, u in mergedTus)
    
    items.sort(reverse=True)
    if duaration and items:
        latestTime = items[0][0]
        startingTime = latestTime - duaration * 24 * 60 * 60
        for i, item in enumerate(items):
            if item[0] <= startingTime:
                items[:] = items[:i]
                break # for i
    
    for lastItem, item in zip([(None, None, None)] + items, items):
        lastT, lastK, lastU = lastItem
        t, k, u = item
        if not (k == lastK and u == lastU):
            if lastU is None or not lastU.startswith(u):
                writefunc(u"%s %s %s\n" % (format_time(t), k, u))


if __name__ == '__main__':
    main()
