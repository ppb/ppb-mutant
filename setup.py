from setuptools import setup


def readme():
    with open('README.md', encoding='utf-8') as file:
        return file.read()


setup(
    name='ppb-mutant',
    version='0.11.2',
    packages=['ppb_mutant', 'ppb_mutant._assets'],
    package_data={'ppb_mutant._assets': ['*.png', '*.txt']},
    install_requires=[
        'ppb>=0.12.0',
    ],
    url='https://github.com/ppb/ppb-mutant',
    license='Artistic-2.0',
    author='Jamie Bliss',
    author_email='jamie@ivyleav.es',
    description='Mutant Standard for PursuedPyBear',
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Artistic License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries",
    ],
    zip_safe=False,
)
