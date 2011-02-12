'''
This __init__ file is present *strictly* so that sphinx's autodoc
extension can find the pubsub1 documentation. It should never
be imported by pubsub.

However, when imported by Sphinx for docstring extraction, we must
add .. to sys.path so that other dependencies can be found (when
imported by pubsub, the pubsub1/pub.py module is seen as living
in the .. folder, from where dependencies can be reached).

:copyright: Copyright 2006-2009 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

'''

# add the parent folder to sys.path because Sphinx needs to import 
# pubsub1 as a module rather than via the mechanism built into pubsub
# module. 
import sys, os
sphinxExtPath = os.path.normpath( os.path.join(__path__[0], '..') )
sys.path.append( sphinxExtPath )
