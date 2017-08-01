APP := myturn
PORT := 5678
export
default: test
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
	if [ -z "$$(readlink -e /var/www/myturn)" ]; then \
	 ln -sf $(PWD) /var/www/myturn; \
	fi
	if [ "$$(readlink -e /var/www/myturn)" != "$(PWD)" ]; then \
	 echo Fix /var/www/myturn to point to this directory! >&2; \
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
	tail -n 50 /var/log/nginx/error.log /var/log/nginx/myturn-error.log
accesslog:
	tail -n 50 /var/log/nginx/access.log /var/log/nginx/myturn-access.log
newlogs:
	sudo rm -f /var/log/nginx/*log
wsgilog applog:
	sudo tail -n 50 /var/log/uwsgi/app/myturn.log
logs:
	sudo tail -n 200 -f /var/log/uwsgi/app/myturn.log \
	 /var/log/nginx/myturn-error.log
	# /var/log/nginx/myturn-access.log
edit: myturn.py html/index.html html/css/style.css
	-vi $+
	# now test:
	./$<
