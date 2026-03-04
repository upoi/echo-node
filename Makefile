PKG_ID      := $(shell yq e ".id" manifest.yaml)
PKG_VERSION := $(shell yq e ".version" manifest.yaml)
IMAGE_TAG   := start9/$(PKG_ID)/main:$(PKG_VERSION)
TS_FILES    := $(shell find scripts -name '*.ts')

.DELETE_ON_ERROR:

all: verify

verify: $(PKG_ID).s9pk
	@start-sdk verify s9pk $(PKG_ID).s9pk
	@echo " [ok] $(PKG_ID).s9pk verified"

install:
	@if [ ! -f /etc/embassy/config.yaml ]; then \
		echo "Error: /etc/embassy/config.yaml not found. Create it with 'host: <IP>' first." && exit 1; \
	fi
	start-cli package install $(PKG_ID).s9pk

clean:
	rm -rf docker-images
	rm -f $(PKG_ID).s9pk
	rm -f scripts/embassy.js

# Bundle TypeScript SDK scripts
scripts/embassy.js: $(TS_FILES)
	deno bundle scripts/embassy.ts scripts/embassy.js

# Build Docker image (x86_64 — models are large so layer cache is critical)
.PHONY: docker-image
docker-image: docker-images/x86_64.tar

docker-images/x86_64.tar: Dockerfile docker_entrypoint.sh FORCE
	@mkdir -p docker-images
	docker buildx build \
		--tag $(IMAGE_TAG) \
		--platform linux/amd64 \
		--file Dockerfile \
		-o type=docker,dest=docker-images/x86_64.tar .

# Pack the s9pk
$(PKG_ID).s9pk: manifest.yaml instructions.md icon.png LICENSE scripts/embassy.js docker-images/x86_64.tar
	@start-sdk pack

.PHONY: all verify install clean FORCE
FORCE:
