SHELL := /bin/bash
APP := pyturn
PORT := 5678
PHANTOMJS_TBZ := https://bitbucket.org/ariya/phantomjs/downloads
PHANTOMJS_TBZ := $(PHANTOMJS_TBZ)/phantomjs-2.1.1-linux-i686.tar.bz2
PHANTOMJS := /usr/src/phantomjs-2.1.1-linux-i686/bin/phantomjs
# HOSTNAME isn't set when used with `sudo make install`
HOSTNAME ?= $(shell hostname)
# add location of phantomjs to PATH
PATH := $(dir $(PHANTOMJS)):$(PATH)
# add location of chromedriver to PATH
PATH := $(HOME)/downloads:$(PATH)
# set npm_config_argv to "alpha" for local (test) installation
npm_config_argv ?= {"remain": ["alpha"]}
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
wsgilog applog:
	sudo tail -n 50 /var/log/uwsgi/app/$(APP)*.log
logs:
	sudo tail -n 200 -f /var/log/uwsgi/app/$(APP)*.log \
	 /var/log/nginx/$(APP)-error.log
edit_all: myturn.py myturn_test.py html/index.html html/css/style.css \
	 html/client.js $(APP).uwsgi $(APP).nginx
	-vi $+
	# now test:
	python3 $<
	python3 -m doctest $<
	pylint3 $<
edit: myturn.py html/index.html html/css/style.css
	-vi $+
	# now test:
	python3 $<
	python3 -m doctest $<
	pylint3 $<
install: install.mk
	$(MAKE) DRYRUN= -f $< siteinstall install
	-$(MAKE) alphapatch
	$(MAKE) restart
alphapatch:
	if [ "$$(git status | sed -n 's/^On branch \(.*\)/\1/p')" = "alpha" -a \
	  "$(HOSTNAME)" = "aspire" ]; then \
	 sed -i 's/^\( *listen 80\)/\1 default_server/' \
	  /etc/nginx/sites-available/pyturn-alpha; \
	fi
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
	touch $@
unittests: $(PHANTOMJS)
	$(MAKE) restart  # start with clean slate
	java -jar ~/Downloads/selenium-server-standalone-3.7.1.jar & \
	 echo $$! > /tmp/testserver.pid
	sleep 5  # wait for Java to start server
	@echo Logging tests to /tmp/unittests.log, please wait...
	-python3 myturn_test.py >/tmp/unittests.log 2>&1
	kill $$(</tmp/testserver.pid)
~/Downloads/$(notdir $(PHANTOMJS_TBZ)):
	cd $(dir $@) && wget $(PHANTOMJS_TBZ)
html/favicon.ico: html/images/myturn-logo.png .FORCE
	convert $< -crop 144x144+0+20 -define icon:auto-resize=64,48,32,16 $@
.FORCE:
