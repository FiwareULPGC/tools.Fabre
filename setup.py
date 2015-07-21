from setuptools import setup
import setuptools
import os
from os import mkdir, umask
from shutil import rmtree
import errno


def get_packages(package):
    """Return root package and all sub-packages."""
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(name='fiware_api_blueprint_renderer',
      version='0.1',
      description='Python module to aid with parsing FIWARE API specification files and rendering them to HTML pages.',
      url='https://github.com/FiwareULPGC/fiware-api-blueprint-renderer',
      author='FIWARE ULPGC',
      author_email='fiware@ulpgc.es',
      license='',
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=[
        'jinja2>=2.7.3',
        'markdown>=2.6.2'
      ],
      entry_points={
        'console_scripts': [
          'fabre = fiware_api_blueprint_renderer.__init__:main',
        ],
        'fiware_api_blueprint_renderer.themes': [
            'default = fiware_api_blueprint_renderer.themes.default_theme'
        ]
      },
      classifiers=[ 
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Documentation',
        'Topic :: Text Processing',
      ],
      zip_safe=False)


# old_umask=umask(000)

# try:
# 	mkdir('/etc/fiware_mkdocs_builder/', 0777)
# except OSError, e:
#     if e.errno != errno.EEXIST:
#         raise e
#     else:
#         rmtree('/etc/fiware_mkdocs_builder/')
#         mkdir('/etc/fiware_mkdocs_builder/', 0777)
#     pass

# try:
# 	mkdir('/var/tmp/fiware_mkdocs_builder_tmp_build/', 0777)
# except OSError, e:
#     if e.errno != errno.EEXIST:
#         raise e
#     else:
#         rmtree('/var/tmp/fiware_mkdocs_builder_tmp_build/')
#         mkdir('/var/tmp/fiware_mkdocs_builder_tmp_build/', 0777)
#     pass

# old_umask= umask(old_umask)
