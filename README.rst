[![Build Status](https://secure.travis-ci.org/tos-kamiya/mondaymorning.png?branch=master)](http://travis-ci.org/tos-kamiya/mondaymorning)

==============
mondaymorning
==============

Mondaymoning is a tool to remember what you were doing on last Friday, on Monday morning.

This tool searches and shows histories of home directory, trash can, and web browsing.

To use `mondaymorning`, just type "python mondaymorning.py" at command line.
The output will looks like the following::

  $ python mondaymorning.py
  2012-04-02 17:22 file ~/bin
  2012-04-02 17:22 file /home/toshihiro
  2012-04-02 17:08 web www.python.jp/doc/release/library/os.path.html#module-os.path
  2012-04-02 16:18 web www.python.jp/doc/2.4/lib/module-os.path.html
  2012-04-02 16:18 web www.google.com/search?q=python+os.path
  2012-04-02 13:49 web www.python.jp/doc/nightly/library/time.html#time.mktime
  2012-04-02 13:48 web www.google.com/search?q=python+time+mktime
  2012-04-02 13:39 trash /home/toshihiro/Downloads/tmp1
  ...

Each line means one of following actions: file creation/modification, file removal, web browsing.

In the output, a day separating line is inserted where day changed.
A dayseparating line is a line which starts with '==='. So you can grep it with a pattern '==='::

  $ mondaymorning.py -d 10 | grep -C1 ===
  2012-08-13 12:19 web togetter.com/li/353759
  === 2012-08-13
  2012-08-10 18:11 web www.2nn.jp
  --
  2012-08-10 10:20 file ~/workspace/astparsertest/bin
  === 2012-08-10
  2012-08-09 20:06 file ~/tmp
  --
  2012-08-09 12:46 web goo.gl/{KK8xa,MGRxr}
  === 2012-08-09
  2012-08-08 17:45 web every-e.com/special
  --
  ...

=============
Installation
=============

To install depending packages::

  $ sudo apt-get install python python-sqlite trash-cli

The trash-cli package is Gnome Trash-can for command line.
This package is optional to mondaymorning, however, 
I recommend to install it and use the 'trash-put' command for deleting files, instead of 'mv',
because trash-put command enables to track a history of file deleting, while
mv command doesn't record anything such a traceable data.

(Mondaymoring is tested by running at command line on Ubuntu 12.04 beta amd64.
Also, it's unit tests are checked with travis-ci.org, for CPython 2.5, 2.6, and 3.2.)

========
License
========

MIT license. ( http://www.opensource.org/licenses/mit-license.html )
