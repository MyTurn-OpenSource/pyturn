default: test
ngrep:
	$@ -dlo . port 5678
test:
	sudo /etc/init.d/uwsgi restart
	-wget --tries=1 --output-document=- http://myturn:5678/
	sudo tail -n 30 /var/log/uwsgi/app/myturn.log
