APP := myturn
PORT := 5678
export
default: test
log:
	sudo tail -n 30 /var/log/uwsgi/app/$(APP).log
ngrep:
	$@ -dlo . port $(PORT)
test: restart fetch log
restart:
	sudo /etc/init.d/uwsgi restart
	sudo /etc/init.d/nginx restart
fetch:
	-wget --tries=1 --output-document=- http://$(APP):$(PORT)/
enable:
	# remember to use parens around each line if running from command line
	# GNU Make runs each in a subprocess so it's not necessary here
	if [ -z "$$(readlink -f /var/www/myturn)" ]; then \
	 ln -sf $(PWD) /var/www/myturn; \
	fi
	if [ "$$(readlink -f /var/www/myturn)" != "$(PWD)" ]; then \
	 echo Fix /var/www/myturn to point to this directory! >&2; \
	fi
	sudo ln -sf $(PWD)/$(APP).ini /etc/uwsgi/apps-available
	cd /etc/uwsgi/apps-enabled && sudo ln -sf ../apps-available/$(APP).ini .
	sudo ln -sf $(PWD)/$(APP).conf /etc/nginx/sites-available
	cd /etc/nginx/sites-enabled/ && sudo ln -sf ../sites-available/$(APP) .
