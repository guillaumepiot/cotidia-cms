import os
from distutils.core import setup
from setuptools import find_packages


VERSION = __import__("cms").VERSION

CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]

install_requires = [
    'Django==1.8.6',
    'Pillow==2.9.0',
    'django-form-utils==1.0.3',
    'django-mptt==0.7.4',
    'django-reversion==1.9.3',
    'djangorestframework==3.2.4',
    'django-codemirror-widget==0.4.0',
]

# taken from django-registration
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('cms'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:

        ################################################################################
        # !!! IMPORTANT !!!                                                            #
        # To get the right prefix, enter the index key of the same                     #
        # value as the length of your package folder name, including the slash.        #
        # Eg: for 'cms/'' , key will be 4                                          #
        ################################################################################

        prefix = dirpath[4:] # Strip "cms/" or "cms\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(
    name="contenttools-cms",
    description="An extensible CMS based on Django, including dynamic page fields in JSON datasets, multilingual localisation and publishing workflow.",
    version=VERSION,
    author="Guillaume Piot",
    author_email="guillaume@cotidia.com",
    url="https://bitbucket.org/guillaumepiot/contenttools-cms",
    package_dir={'cms': 'cms'},
    packages=packages,
    package_data={'cms': data_files},
    include_package_data=True,
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)