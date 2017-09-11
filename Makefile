APP := myturn
PORT := 5678
export
default: test
ngrep:
	$@ -dlo . port $(PORT)
test: restart fetch applog
restart:
	sudo /etc/init.d/uwsgi restart
	sudo /etc/init.d/nginx restart
fetch:
	-wget --tries=1 --output-document=- http://$(APP):$(LEGACY_PORT)/
enable:
	# remember to use parens around each line if running from command line
	# GNU Make runs each in a subprocess so it's not necessary here
	if [ -z "$$(readlink -e /var/www/$(APP))" ]; then \
	 ln -sf $(PWD) /var/www/$(APP); \
	fi
	if [ "$$(readlink -e /var/www/$(APP))" != "$(PWD)" ]; then \
	 echo Fix /var/www/$(APP) to point to this directory! >&2; \
	 false; \
	fi
	sudo ln -sf $(PWD)/$(APP).ini /etc/uwsgi/apps-available
	cd /etc/uwsgi/apps-enabled && \
	  sudo ln -sf ../apps-available/$(APP).ini .
	sudo ln -sf $(PWD)/$(APP).conf /etc/nginx/sites-available
	cd /etc/nginx/sites-enabled/ && \
	  sudo ln -sf ../sites-available/$(APP).conf .
reload: newlogs enable restart
errorlog:
	tail -n 50 /var/log/nginx/error.log /var/log/nginx/$(APP)-error.log
accesslog:
	tail -n 50 /var/log/nginx/access.log /var/log/nginx/$(APP)-access.log
newlogs:
	sudo rm -f /var/log/nginx/*log
wsgilog applog:
	sudo tail -n 50 /var/log/uwsgi/app/$(APP).log
logs:
	sudo tail -n 200 -f /var/log/uwsgi/app/$(APP).log \
	 /var/log/nginx/$(APP)-error.log
edit: $(APP).py html/index.html html/css/*.css html/client.js \
	$(APP).ini $(APP).conf
	-vi $+
	# now test:
	python3 $<
install: install.mk
	$(MAKE) -f $<
