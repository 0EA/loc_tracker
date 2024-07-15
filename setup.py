from setuptools import setup, find_packages

setup(
    name='loc_tracker',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'geopy',
        'shapely'
    ],
    author='Nurullah Eren',
    author_email='n.erenacar13@gmail.com',
    description='UAV data processing and scoring package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/0ea/loc_tracker',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
