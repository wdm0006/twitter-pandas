Contributing Code
=================

Twitter-pandas is a python library for analyzing twitter-data with pandas.  Our goal is twofold:

 * To make the analysis of twitter based data simple, fast, and downright pleasant.
 * To give developers interested in data analysis a simple interface to datasets that they understand and can get pretty easily.
 
With that in mind, we welcome and in fact would love some help.

How to Contribute
=================

The preferred workflow to contribute to git-pandas is:

 1. Fork this repository into your own github account.
 2. Clone the fork on your account onto your local disk:
 
    $ git clone git@github.com:YourLogin/twitter-pandas.git
    $ cd twitter-pandas
    
 3. Create a branch for your new awesome feature, do not work in the master branch:
 
    $ git checkout -b new-awesome-feature
    
 4. Write some code, or docs, or tests.
 5. When you are done, submit a pull request.
 
Guidelines
==========

Twitter-pandas is still a very young project, but we do have a few guiding principles:

 1. Enforce and encourage responsible usage of twitter APIs (people shouldn't be getting banned because of bad code here)
 2. Write detailed docstrings in sphinx format
 3. Slow or potentially memory intensive functions should have a limit option
 4. Focus on data gathering / analysis first, not on posting/tweeting/outward bound tasks.

Running Tests
=============

Test coverage is non-existant right now, so help out by writing tests for new code. To run the tests, use:

    $ nosetests --with-coverage
    $ coverage html
    
Easy Issues / Getting Started
=============================

Implement simple pass-thru methods returning a dataframe for the tweepy methods grouped under:

 * status methods
 * direct message methods
 * friendship methods
 * block methods
 * saved search methods
 * help methods
 * geo methods