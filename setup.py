from setuptools import setup, find_packages

install_reqs = [
    'json',
    'numpy',
    'os',
    'pandas',
    'pyfirmata',
    'serial'
]

with open('README.md', 'r') as file:
    readme = file.read()

setup(
    name='sys2py',
    version='1.0',
    description='Python interface for external systems connected via a serial port or Arduino',
    long_description=readme,
    url='https://github.com/minel-arinel/sys2py',
    author='Minel Arinel',
    author_email='',
    license='MIT',
    packages=['sys2py'],
    python_requires='>=3.7',
    install_requires=install_reqs
)
