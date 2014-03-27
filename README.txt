This is a CSE 491/Web dev project; see http://msu-web-dev.readthedocs.org/.

1. Running server.py on arctic.
===============================

In a subdirectory on arctic.cse.msu.edu, create a Python `virtualenv
<http://www.virtualenv.org/en/latest/>`__ using Python 2.7::

   python2.7 -m virtualenv cse491.env

Now, activate this virtualenv::

   source cse491.env/bin/activate.csh

(From now on, you'll want to make sure to have this virtualenv active
whenever you're working on server.py.)

Next, go to your cse491-serverz directory and run server.py::

   python server.py

Use CTRL-C to quit the server.
