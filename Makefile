default: test
log:
	sudo tail -n 30 /var/log/uwsgi/app/myturn.log
ngrep:
	$@ -dlo . port 5678
test: restart fetch log
restart:
	sudo /etc/init.d/uwsgi restart
fetch:
	-wget --tries=1 --output-document=- http://myturn:5678/
