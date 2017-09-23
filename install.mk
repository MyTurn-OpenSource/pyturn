SHELL := /bin/bash
NODE_ENV := $(shell nodejs -e \
 'process.stdout.write(JSON.stringify(process.env))')
NPM_CONFIG_ARGV := $(shell nodejs -e \
 'process.stdout.write(process.env.npm_config_argv)')
PACKAGE := $(shell nodejs -e \
 'process.stdout.write(JSON.parse(process.env.npm_config_argv)["remain"][0])')
BRANCH := $(shell echo $(PACKAGE) | cut -d\# -f2)
# we're only interested in specially named branches, to determine port number
BRANCH := $(findstring $(BRANCH), alpha beta)
ifeq ($(strip $(BRANCH)),)
 BRANCH := release
endif
APP := pyturn
SERVICE := $(APP)-$(BRANCH)
# ports are even numbers so we can have a status port at port+1
ALPHA_PORT := 5684
BETA_PORT := 5682
RELEASE_PORT := 5680
LEGACY_PORT := 5678
LEGACY_STATUS_PORT := 5679
SERVER_PORT := $($(shell echo $(BRANCH) | tr a-z A-Z)_PORT)
STATUS_PORT := $(shell echo $$(($(SERVER_PORT) + 1)))
NGINX_CONFIG := /etc/nginx
UWSGI_CONFIG := /etc/uwsgi
SITE_ROOT := /usr/local/jcomeauictx/$(SERVICE)
SITE_CONFIG := $(NGINX_CONFIG)/sites-available/$(SERVICE)
SITE_ACTIVE := $(NGINX_CONFIG)/sites-enabled/$(SERVICE)
APP_CONFIG := $(UWSGI_CONFIG)/apps-available/$(SERVICE)
APP_ACTIVE := $(UWSGI_CONFIG)/apps-enabled/$(SERVICE).ini
TIMESTAMP := $(shell date +%Y%m%d%H%M%S)
DRYRUN ?= --dry-run  # for rsync
DELETE ?= --delete
export
set env:
	$@
install: $(APP_ACTIVE) $(SITE_ACTIVE) restart_uwsgi restart_nginx
siteinstall: | $(SITE_ROOT)
	rsync -avcz $(DRYRUN) $(DELETE) \
	 --exclude=configuration --exclude='.git*' \
	 . $(SITE_ROOT)/
$(SITE_ROOT):
	mkdir -p $@
$(SITE_ACTIVE): $(SITE_CONFIG)
	ln -sf $< $@
$(APP_ACTIVE): $(APP_CONFIG)
	ln -sf $< $@
/tmp/$(SERVICE).%: $(APP).% .FORCE
	cp -f $< $@
	sed -i -e "s/$(LEGACY_PORT)/$(SERVER_PORT)/" \
	 -e "s/legacy/$(BRANCH)/g" \
	 -e "s/$(LEGACY_STATUS_PORT)/$(STATUS_PORT)/" \
	 -e "s%/jcomeauictx/myturn/%/jcomeauictx/$(SERVICE)/%" \
	 $@
ifeq (release,$(BRANCH))
	if [ -f /etc/nginx/sites-enabled/default ]; then \
	 echo WARNING: Removing old default configuration >&2; \
	 rm -f /etc/nginx/sites-enabled/default; \
	fi
	if [ -f /etc/nginx/sites-enabled/$(APP) ]; then \
	 echo WARNING: Removing old $(APP) configuration >&2; \
	 rm -f /etc/nginx/sites-enabled/$(APP); \
	fi
	# make new default a redirect to the release
	@echo WARNING: Redirecting default to uwsgi-release.myturn.mobi >&2
	cp -f default.nginx /etc/nginx/sites-available/$(APP)-default
	cd /etc/nginx/sites-enabled && \
	 ln -s ../sites-available/$(APP)-default .
	@echo WARNING: If you have another default, nginx will not start >&2
endif
$(SITE_CONFIG): /tmp/$(SERVICE).nginx .FORCE
	if [ -e "$@" ]; then \
	 if diff -q $< $@; then \
	  echo $@ unchanged >&2; \
	 else \
	  echo Saving $@ to $@.$(TIMESTAMP) >&2; \
	  mv $@ $@.$(TIMESTAMP); \
	 fi; \
	fi
	[ -e "$@" ] || mv $< $@
$(APP_CONFIG): /tmp/$(SERVICE).uwsgi .FORCE
	if [ -e "$@" ]; then \
	 if diff -q $< $@; then \
	  echo $@ unchanged >&2; \
	 else \
	  echo Saving $@ to $@.$(TIMESTAMP) >&2; \
	  mv $@ $@.$(TIMESTAMP); \
	 fi; \
	fi
	[ -e "$@" ] || mv $< $@
restart_%:
	/etc/init.d/$* restart
.FORCE:
