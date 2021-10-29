SHELL := /bin/bash
APP := pyturn
BRANCH := $(shell git branch --no-color | awk '$$1 ~ /^\*$$/ {print $$2}')
PORT := 5678
# a bunch of shared library packages from wheezy and jessie are needed
# for phantomjs, even though the binary is statically linked:
# sudo apt-get install libpng12-0 libssl1.0.0 libicu52 libhyphen0 libwebp5
PHANTOMJS_VERSION := phantomjs-2.5.0-beta-ubuntu-trusty
PHANTOMJS_PACKAGE := phantomjs-2.5.0-beta-linux-ubuntu-trusty-x86_64
PHANTOMJS_TBZ := https://bitbucket.org/ariya/phantomjs/downloads
PHANTOMJS_TBZ := $(PHANTOMJS_TBZ)/$(PHANTOMJS_PACKAGE).tar.gz
PHANTOMJS := /usr/src/$(PHANTOMJS_VERSION)/bin/phantomjs
# HOSTNAME isn't set when used with `sudo make install`
HOSTNAME ?= $(shell hostname)
# add location of phantomjs to PATH
PATH := $(dir $(PHANTOMJS)):$(PATH)
# add location of chromedriver to PATH
PATH := $(HOME)/downloads:$(PATH)
# add location of adb to PATH
ANDROID_SDK := /usr/local/src/android/adt-bundle-linux-x86_64-20130717/sdk
PATH := $(ANDROID_SDK)/platform-tools:$(PATH)
TODAY ?= $(shell date +%Y-%m-%d)
# XTODAY for nginx
XTODAY = $(shell date +%Y/%m/%d)
# result of `make unittests` goes to ~/downloads for LASTLOG
TESTLOG ?= ~/downloads/apptest.log
# last client log using Chrome remote Android debugger, saved to ~/downloads
# don't use := or ?= for this, `touch` the log you want if necessary
LASTLOG = $(shell ls -rt ~/downloads/*.log 2>/dev/null | tail -n 1)
# nginx errorlog shows connection errors
ERRORLOG := /var/log/nginx/pyturn-error.log
BROWSER ?= chrome
export
default: test
ngrep:
	$@ -dlo . port $(PORT)
test: restart fetch applog
restart:
	sudo /etc/init.d/uwsgi restart
	sudo /etc/init.d/nginx restart
fetch:
	-wget --tries=1 --output-document=- http://$(APP):$(PORT)/
reload: newlogs restart
errorlog:
	tail -n 50 /var/log/nginx/error.log /var/log/nginx/$(APP)-error.log
accesslog:
	tail -n 50 /var/log/nginx/access.log /var/log/nginx/$(APP)-access.log
newlogs:
	sudo rm -f /var/log/nginx/*log
# Have root add you to adm group: usermod -a -g adm luser
wsgilog applog:
	tail -n 50 /var/log/uwsgi/app/$(APP)-$(BRANCH).log
logs:
	tail -n 200 -f /var/log/uwsgi/app/$(APP)-$(BRANCH).log \
	 /var/log/nginx/$(APP)-error.log
edit_all: myturn.py apptest.py html/index.html html/css/style.css \
	 html/client.js $(APP).uwsgi $(APP).nginx
	-vi $+
	# now test:
	python3 $<
	python3 -m doctest $<
	$(MAKE) html/client.js.test
	pylint3 --disable=locally-disabled $<
edit: myturn.py html/index.html html/css/style.css
	-vi $+
	# now test:
	python3 $<
	python3 -m doctest $<
	pylint3 --disable=locally-disabled $<
install: install.mk
	$(MAKE) DRYRUN= -f $< siteinstall install
	$(MAKE) restart
	cp -f pyturn.cron /etc/cron.d/pyturn
%.ssh:
	# must first set up ~/.ssh/config:
	# Host droplet
	# User root
	# StrictHostKeyChecking no
	# UserKnownHostsFile /dev/null
	# and put an entry for droplet in /etc/hosts, e.g.:
	# 12.34.56.78 droplet
	sudo sed -i \
	 's/^[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+\s\(droplet.*\)/$* \1/' \
	 /etc/hosts
	ssh root@droplet
set:
	$@
$(PHANTOMJS): ~/Downloads/$(notdir $(PHANTOMJS_TBZ))
	cd /usr/src/ && tar xvf $<
	chmod +x $@
	touch $@
unittests: $(PHANTOMJS)
	$(MAKE) restart  # start with clean slate
	-java -jar ~/Downloads/selenium-server-standalone-3.12.0.jar & \
	 echo $$! > /tmp/testserver.pid
	sleep 5  # wait for Java to start server
	@echo Logging tests to $(TESTLOG), please wait...
	-python3 apptest.py >$(TESTLOG) 2>&1
	kill $$(</tmp/testserver.pid)
	$(MAKE) mergelogs
	tail -n 50 $(LASTLOG)
	@echo Tests were logged to $(TESTLOG)
~/Downloads/$(notdir $(PHANTOMJS_TBZ)):
	cd $(dir $@) && wget $(PHANTOMJS_TBZ)
html/favicon.ico: html/images/myturn-logo.png .FORCE
	convert $< -crop 144x144+0+20 -resize 16x16 /tmp/myturn-icon.16.png
	convert $< -crop 144x144+0+20 -resize 32x32 /tmp/myturn-icon.32.png
	convert $< -resize 48x48 /tmp/myturn-icon.48.png
	convert $< -resize 64x64 /tmp/myturn-icon.64.png
	convert /tmp/myturn-icon.*.png -background none $@

.FORCE:
mergelogs:  # combine output of server and client side debugging logs
	# filters out date because it's in different formats
	cat <(sudo sed -n 's/^$(TODAY) \([0-9:,]\+:DEBUG:.*\)/\1/p' \
	 /var/log/uwsgi/app/pyturn-alpha.log) \
	 <(sed -n 's%^$(XTODAY) %%p' $(ERRORLOG)) \
	 <(sed -n 's/$(TODAY) //p' $(LASTLOG) | \
	  egrep -v ':Finished Request|/wd/hub/session') | sort
%.js.test: $(PHANTOMJS)
	$< --debug=true $(@:.test=)
js.test: $(PHANTOMJS)
	$<
interactive: $(PHANTOMJS)
	python3 -i -c'from apptest import *'
adbshell:
	adb shell
logcat:
	adb logcat
shell:
	bash
doctests: myturn.doctest
%.doctest: %.py
	python3 -m doctest $<
view: html/index.html
	grep -v noscript $< > /tmp/index.html
	$(BROWSER) /tmp/index.html
