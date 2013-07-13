## Process this file with automake to produce Makefile.in
## Created by Anjuta

SUBDIRS = src 

flipbuqdocdir = ${prefix}/doc/flipbuq
flipbuqdoc_DATA = \
	README\
	COPYING\
	AUTHORS\
	ChangeLog\
	INSTALL\
	NEWS


EXTRA_DIST = $(flipbuqdoc_DATA)


# Remove doc directory on uninstall
uninstall-local:
	-rm -r $(flipbuqdocdir)
