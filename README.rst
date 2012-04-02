==============
mondaymorning
==============

Mondaymoning is a tool to remember what you were doing on last Friday, on Monday morning.

This tool searches and shows histories of home directory, trash can, and web browsing.

To use `mondaymorning`, just type "python mondaymorning.py" at command line.
The output will looks like the following::

  $ python mondaymorning.py
  2012-04-02 13:49:52 file /home/toshihiro
  2012-04-02 13:49:14 web http://www.python.jp/doc/nightly/library/time.html#time.mktime
  2012-04-02 13:48:46 web http://www.python.jp/doc/nightly/library/time.html
  2012-04-02 13:48:44 web q=python+time+mktime
  2012-04-02 13:39:11 trash /home/toshihiro/Downloads/tmp1
  2012-04-02 13:39:11 file /home/toshihiro/Downloads
  2012-04-02 12:30:49 web http://maps.google.co.jp
  2012-04-02 12:30:47 web q=gogolemap
  2012-04-02 11:19:56 web q=raw_unicode_escape
  2012-04-02 11:18:55 web http://linuxfree.ma-to-me.com/archives/000333.html
  2012-04-02 11:18:20 web q=python+urlib2 q=python+urlib2+%
  2012-04-02 11:18:01 web http://docs.python.org/library/urllib2.html
  2012-04-02 11:17:58 web q=python+urlib2
  2012-04-02 11:17:37 web q=python+url+decode
  2012-04-02 11:12:37 web http://home.kendomo.net/board/decode
  2012-04-02 11:12:15 web http://forum.mozilla.gr.jp/?mode=al2&namber=21337&rev=&&KLOG=133
  2012-04-02 11:12:05 web q=firefox+urldecode
  2012-04-02 10:17:14 web http://www.nifty.com/mail
  2012-04-02 09:58:08 trash /media/SUB/kamiya/tmp.txt
  2012-04-02 09:13:39 web http://auth.fun.ac.jp/netlogin/Login.html
  2012-03-30 19:24:27 web https://github.com/tos-kamiya/wwi/blob/master/src/wwi.py
  ...

Each line means one of following actions: file creation/modification, file removal, web browsing.

=============
Installation
=============

(Mondaymoring is tested on Ubuntu 12.04 beta amd64.)

To install depending packages::

  $ sudo apt-get install python python-sqlite trash-cli

The trash-cli package is Gnome Trash-can for command line.
This package is optional to mondaymorning, however, 
I recommend to install it and use the 'trash' command in deleting files, instead of 'mv',
because trash-can enables to track a history of deleted files.

