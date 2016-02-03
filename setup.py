from distutils.core import setup

setup(
    name='PaPI',
    version='1.3',
    packages=['papi'],
    url='https://github.com/TUB-Control/PaPI',
    license='GPL v3',
    author='TU-Berlin, FG Regelungssysteme',
    author_email='github@control.tu-berlin.de',
    description='PaPI',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3',
        'Programming Language :: Python :: 3.4'
    ],
    install_requires=['numpy', 'socketio_client', 'PyQt5']
)
