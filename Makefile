APP := pyturn
PORT := 5678
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
edit: myturn.py html/index.html html/css/*.css html/client.js \
	$(APP).uwsgi $(APP).nginx
	-vi $+
	# now test:
	python3 $<
install: install.mk
	$(MAKE) DRYRUN= -f $< siteinstall install
	$(MAKE) restart
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
env set:
	$(MAKE) -f install.mk $@
