TOPDIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
TEMPLATES := $(shell find ${TOPDIR}/coco/templates -name '*.html')
SOURCE := $(shell find ${TOPDIR}/coco -name '*.py')
LOCALEDIR = ${TOPDIR}/coco/locale/fr/LC_MESSAGES

all: translations

translations: ${LOCALEDIR}/django.mo

${LOCALEDIR}/django.mo: ${LOCALEDIR}/django.po
	cd ${TOPDIR}/coco ; django-admin compilemessages

${LOCALEDIR}/django.po: ${SOURCE} ${TEMPLATES}
	cd ${TOPDIR}/coco ; django-admin makemessages --no-wrap --locale fr

upload:
	${TOPDIR}/upload

