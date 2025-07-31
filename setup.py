from setuptools import setup, find_packages


setup(
    name='PV-tool',
    version='0.1.4',
    author='Tjalda Deenekamp en Nathan Gebraad',
    author_email='leo.kwakman@arcadis.com',
    description='Functionalities concerning the PV-tool.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TjaldaDeenekamp/PV-tool',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=['pandas',
                      'numpy',
                      'scipy',
                      'matplotlib',
                      'plotly',
                      'openpyxl',
                      'gitpython',
                      'pandas_schema',
                      'xlsxwriter'
                      ],
)
