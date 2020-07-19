import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
PACKAGE_NAME = 'pysankey2'
VERSION = '0.1.0'
AUTHOR = 'Zijie Shen'
AUTHOR_EMAIL = 'szjshuffle@foxmail.com'
URL = 'https://github.com/SZJShuffle/pySankey2'
LICENSE = ' LGPL-3.0 License'

DESCRIPTION = 'Static sankey diagrams with matplotlib.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

with open(HERE / "requirements.txt", "r") as fh:
    require = fh.readlines()
INSTALL_REQUIRES =  [x.strip() for x in require]

PACKAGES=['pysankey2','pysankey2.test']

CLASSIFIERS = [
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Multimedia :: Graphics',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS'
]

if __name__ == "__main__":
    setup(name=PACKAGE_NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESC_TYPE,
        author=AUTHOR,
        license=LICENSE,
        author_email=AUTHOR_EMAIL,
        url=URL,
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
        packages=PACKAGES,
        classifiers=CLASSIFIERS
        )
