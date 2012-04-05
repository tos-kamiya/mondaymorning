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

========
License
========

MIT license. ( http://www.opensource.org/licenses/mit-license.html )
