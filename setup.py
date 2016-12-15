from setuptools import find_packages, setup


setup(
    name="cotidia-cms",
    description="CMS for Cotidia base project.",
    version="1.0",
    author="Guillaume Piot",
    author_email="guillaume@cotidia.com",
    url="https://code.cotidia.com/cotidia/cms/",
    packages=find_packages(),
    package_dir={'cms': 'cms'},
    package_data={
        'cotidia.cms': [
            'templates/admin/*.html',
            'templates/admin/cms/*.html',
            'templates/admin/cms/dataset/*.html',
            'templates/admin/cms/includes/*.html',
            'templates/cms/*.html'
        ]
    },
    namespace_packages=['cotidia'],
    include_package_data=True,
    install_requires=[
        'django>=1.10.2',
        'django-form-utils==1.0.3',
        'djangorestframework>=3.5.1',
        'django-mptt==0.8.6',
        'django-reversion==2.0.8',
        'Pillow==3.1.1',
        'django-codemirror-widget==0.4.0',
    ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],
)
