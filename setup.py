import sys

from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

PACKAGE = "pyclick"
PACKAGE_NAME = "python-click"
VERSION = '0.0.1'
DESCRIPTION = 'Integration Click with Django'
LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'
CLASSIFIERS = [
                  'Development Status :: 5 - Production/Stable',
                  'Environment :: Web Environment',
                  'Framework :: Django',
                  'Framework :: Django :: 3.0',
                  'Framework :: Django :: 3.1',
                  'Framework :: Django :: 3.2',
                  'Framework :: Django :: 4.0',
                  'Framework :: Django :: 4.1',
                  'Intended Audience :: Developers',
                  'License :: OSI Approved :: BSD License',
                  'Operating System :: OS Independent',
                  'Programming Language :: Python',
                  'Programming Language :: Python :: 3',
                  'Programming Language :: Python :: 3.6',
                  'Programming Language :: Python :: 3.7',
                  'Programming Language :: Python :: 3.8',
                  'Programming Language :: Python :: 3.9',
                  'Programming Language :: Python :: 3.10',
                  'Programming Language :: Python :: 3 :: Only',
                  'Topic :: Internet :: WWW/HTTP',
              ],
# Setting up
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Sirojiddin Yakubov",
    author_email="yakubov9791999@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    python_requires=">=3.5",
    packages=find_packages(),
    install_requires=['requests', 'django', 'djangorestframework'],
    keywords=['python', 'click', 'django', 'django rest framework'],
    url="https://github.com/yakubov9791999/python-click",
    classifiers=CLASSIFIERS,
    project_urls={
        'Funding': 'https://fund.django-rest-framework.org/topics/funding/',
        'Source': 'https://github.com/encode/django-rest-framework',
        'Changelog': 'https://www.django-rest-framework.org/community/release-notes/',
    },
)

if sys.argv[-1] == "publish":
    print('ok')
    # os.system("python setup.py sdist bdist_wheel upload")
    # sys.exit()
