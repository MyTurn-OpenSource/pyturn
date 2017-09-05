SHELL := /bin/bash
NODE_ENV := $(shell node -e \
 'process.stdout.write(JSON.stringify(process.env))')
NPM_CONFIG_ARGV := $(shell node -e \
 'process.stdout.write(process.env.npm_config_argv)')
PACKAGE := $(shell node -e \
 'process.stdout.write(JSON.parse(process.env.npm_config_argv)["remain"][0])')
BRANCH := $(shell echo $(PACKAGE) | cut -d\# -f2)
# we're only interested in specially named branches, to determine port number
BRANCH := $(findstring $(BRANCH), alpha beta baseline)
ifeq ($(strip $(BRANCH)),)
 BRANCH := release
endif
APP := myturn
SERVICE := $(APP)-$(BRANCH)
BACKEND := $(APP)@$(BRANCH)
ALPHA_PORT := 5686
BETA_PORT := 5684
BASELINE_PORT := 5682
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
