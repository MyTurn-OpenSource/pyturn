SHELL := /bin/bash
NODE_ENV := $(shell node -e \
 'process.stdout.write(JSON.stringify(process.env))')
NPM_CONFIG_ARGV := $(shell node -e \
 'process.stdout.write(process.env.npm_config_argv)')
PACKAGE := $(shell node -e \
 'process.stdout.write(JSON.parse(process.env.npm_config_argv)["remain"][0])')
BRANCH := $(shell echo $(PACKAGE) | cut -d\# -f2)
# we're only interested in specially named branches, to determine port number
BRANCH := $(findstring $(BRANCH), alpha beta)
ifeq ($(strip $(BRANCH)),)
 BRANCH := release
endif
APP := pyturn
SERVICE := $(APP)-$(BRANCH)
BACKEND := $(APP)@$(BRANCH)
ALPHA_PORT := 5684
BETA_PORT := 5682
RELEASE_PORT := 5680
LEGACY_PORT := 5678
SERVER_PORT := $($(shell echo $(BRANCH) | tr a-z A-Z)_PORT)
NGINX_CONFIG := /etc/nginx
SITE_ROOT := /var/www/$(SERVICE)
SITE_CONFIG := $(NGINX_CONFIG)/sites-available/$(SERVICE)
SITE_ACTIVE := $(NGINX_CONFIG)/sites-enabled/$(SERVICE)
TIMESTAMP := $(shell date +%Y%m%d%H%M%S)
DRYRUN ?= --dry-run  # for rsync
DELETE ?= --delete
export
set env:
	$@
install: /etc/systemd/system/$(APP)@$(BRANCH).service $(SITE_ACTIVE) \
 restart_$(BACKEND) restart_nginx
/etc/systemd/system/%: /tmp/%
	mv -f $< $@
/tmp/$(APP)@%.service: $(APP)@.service .FORCE
	cp -f $< $@
	sed -i "s/$(LEGACY_PORT)/$(SERVER_PORT)/" $@
siteinstall: | $(SITE_ROOT)
	rsync -avcz $(DRYRUN) $(DELETE) \
	 --exclude=configuration --exclude='.git*' \
	 . $(SITE_ROOT)/
$(SITE_ROOT):
	mkdir -p $@
$(SITE_ACTIVE): $(SITE_CONFIG)
	cd $(dir $@) && ln -sf ../sites-available/$(notdir $<) .
/tmp/$(SERVICE).nginx: $(APP).nginx .FORCE
	cp -f $< $@
	sed -i -e "s/$(LEGACY_PORT)/$(SERVER_PORT)/" \
	 -e "s/legacy/$(BRANCH)/g" \
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
	@echo WARNING: Redirecting default to release.myturn.mobi >&2
	cp -f default.nginx /etc/nginx/sites-available/$(APP)-default
	cd /etc/nginx/sites-enabled && \
	 ln -s ../sites-available/$(APP)-default .
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
restart_%:
	-systemctl stop $*
	systemctl daemon-reload  # in case configuration changed
	systemctl enable $*
	systemctl start $*
diff:
	diff -r -x '.git*' .. /var/www/$(SERVICE)
.FORCE:
