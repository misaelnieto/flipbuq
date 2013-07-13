## Process this file with automake to produce Makefile.in
## Created by Anjuta


uidir = $(pkgdatadir)/ui
ui_DATA = flipbuq.ui


## The main script
bin_SCRIPTS = flipbuq.py

## Directory where .class files will be installed
flipbuqdir = $(pythondir)/flipbuq


flipbuq_PYTHON = \
	flipbuq.py


EXTRA_DIST = $(ui_DATA)


# Remove ui directory on uninstall
uninstall-local:

	-rm -r $(uidir)

	-rm -r $(pkgdatadir)
