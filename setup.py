from setuptools import setup

install_reqs = [
    'json',
    'numpy',
    'os',
    'pandas',
    'pyfirmata',
    'serial'
]

setup(
    name='sys2py',
    version='1.0',
    description='Python interface for external systems connected via a serial port or Arduino',
    url='',
    author='Minel Arinel',
    author_email='',
    license='MIT',
    packages=['sys2py'],
    python_requires='>=3.7',
    install_requires=install_reqs
)
