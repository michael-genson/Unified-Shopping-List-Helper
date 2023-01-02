ENV ?= dev
SAM_ROOT = deploy

deployment: update-manifest
	poetry export -f requirements.txt --output Lambda/requirements.txt
	sam build \
		--template-file $(SAM_ROOT)/template.yaml \
		--config-file samconfig-$(ENV).toml \

	sam deploy \
		--config-file $(SAM_ROOT)/samconfig-$(ENV).toml \

update-manifest:
	ask smapi update-skill-manifest -s ${SKILL_ID} -g development --manifest "file:${SAM_ROOT}/skill-${ENV}.json"
