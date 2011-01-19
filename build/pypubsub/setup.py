#from distutils.core import setup
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

# use the module docs as the long description: 
import pubsub2
longDesc = pubsub2.__doc__.split(':Author:')[0]
longDesc = """
This provides a simple but versatile messaging system, ideal for decoupling
parts of your application: senders and listeners don't need to know about
each other.
        
Version 2 provides pubsub2, which should be used instead of pubsub:

- pubsub2 provides better handling of exceptions
- allows tools like pylint/pychecker to verify validity of message types
- facilitates the documentation of message types and message data
- supports customizable logging (incl no logging, the default)
- support debugging of the send/receive dispatches

The only real change from pubsub is that class are used instead of 
strings for the message topics, and a whole whack of code is no 
longer needed (tree and its traversal, dictionary of weak references, 
etc). 

Version 1 is still available as pubsub, for backwards compatibility, 
but it is depracated. 

Todo:

- include the traceback in the exception info
- support subtopic access in supertopic messages
"""

#print longDesc[0]

setup(
    name         = 'PyPubSub',
    version      = '2.0',
    description  = 'Python Publish-Subscribe Module',
    author       = 'Oliver Schoenborn et al',
    author_email = 'oliver.schoenborn@utoronto.ca',
    py_modules   = [
        'pubsub', 
        'pubsub2', 
        'weakmethod',
    ],
    scripts      = ['testpubsub.py'],
    license      = "PSF",
    keywords     = "publish subscribe observer pattern signal signals event events message messages messaging",
    classifiers  = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description = longDesc
)


