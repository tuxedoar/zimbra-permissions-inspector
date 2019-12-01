from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='zimbra-permissions-inspector',
    version='0.1',
    description='Query sending permissions on a Zimbra server',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tuxedoar/zimbra-permissions-inspector',
    author='tuxedoar',
    author_email='tuxedoar@gmail.com',
    packages=['zimbra_permissions_inspector'],
    python_requires='>=3.4',
    scripts=["zimbra_permissions_inspector/_version.py"],
    entry_points={
        "console_scripts": [
        "zimbra-permissions-inspector = zimbra_permissions_inspector.zimbra_permissions_inspector:main",
        ],
    },
    install_requires=[
    'python-ldap'
    ],

    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        ],
)
