import os

from setuptools import find_packages, setup


def package_files(dirs):
    paths = []
    for directory in dirs:
        for (path, directories, filenames) in os.walk(directory):
            # Only keep the last directory of the path
            path = path.replace(directory, directory.split("/")[-1])
            for filename in filenames:
                paths.append(os.path.join(path, filename))
    return paths


template_files = package_files(["cotidia/cms/templates", "cotidia/cms/static"])

setup(
    name="cotidia-cms",
    description="CMS for Cotidia base project.",
    version="1.0",
    author="Guillaume Piot",
    author_email="guillaume@cotidia.com",
    url="https://code.cotidia.com/cotidia/cms/",
    packages=find_packages(),
    package_dir={"cms": "cms"},
    package_data={"cotidia.cms": template_files},
    namespace_packages=["cotidia"],
    include_package_data=True,
    install_requires=[
        "django==2.2",
        "django-form-utils==1.0.3",
        "djangorestframework==3.13",
        "django-mptt==0.9.1",
        "django-reversion==2.0.13",
        "django-codemirror-widget==0.4.1",
    ],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
)
