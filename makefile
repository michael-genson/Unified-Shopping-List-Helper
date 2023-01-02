ENV ?= dev
SAM_ROOT = deploy

update-manifest:
	ask smapi update-skill-manifest -s ${SKILL_ID} -g development --manifest "file:${SAM_ROOT}/skill-${ENV}.json"

update-lambda:
	poetry export -f requirements.txt --output Lambda/requirements.txt
	sam build \
		--template-file $(SAM_ROOT)/template.yaml \
		--config-file samconfig-$(ENV).toml \

	sam deploy \
		--config-file $(SAM_ROOT)/samconfig-$(ENV).toml \

deployment: update-manifest update-lambda