#from distutils.core import setup
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

# use the module docs as the long description: 
longDesc = '' #file('cheese.txt', 'r').read()

packages = find_packages('src')
#print packages

setup(
    name         = 'PyPubSub',
    version      = '3.1.1b1',
    description  = 'Python Publish-Subscribe Package',
    author       = 'Oliver Schoenborn et al',
    author_email = 'oliver.schoenborn@utoronto.ca',
    url          = 'http://pubsub.wiki.sourceforge.net',
    download_url = 'http://sourceforge.net/project/showfiles.php?group_id=197063',
    packages     = packages,
    package_dir  = {'': 'src'},
    scripts      = [],
    license      = "BSD",
    #include_package_data = True,
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


