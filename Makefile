APP ?= smaystr-bot
REGISTRY ?= quay.io/smaystr
VERSION = $(shell git describe --tags --abbrev=0 2>/dev/null || echo dev)-$(shell git rev-parse --short HEAD)
GOARCH ?= amd64
GOOS ?= linux
# Comma-separated list as required by docker buildx (container images support only linux)
PLATFORMS = linux/amd64,linux/arm64

# Ensure tempdir exists before any target runs
.PHONY: ensure-tmp

# Run Go-based temp directory setup helper
tmp-setup:
	@go run tools/tmp_setup.go

ensure-tmp:
	@mkdir -p "$(CURDIR)/.tmp" && chmod -R 1777 "$(CURDIR)/.tmp"
	@# Встановлюємо TMPDIR і для поточного процесу make, і для bash
	@export TMPDIR="$(CURDIR)/.tmp" && echo 'export TMPDIR="$(CURDIR)/.tmp"' > .tmprc
	@echo "Created $(CURDIR)/.tmp"
	@# Робимо додаткові каталоги на всякий випадок
	@mkdir -p /tmp || mkdir -p tmp || true 
	@chmod 1777 /tmp tmp 2>/dev/null || true

# Викликаємо Go-хелпер для temp dir
	@go run tools/tmp_setup.go || true

format: ensure-tmp
	gofmt -s -w ./

deps: ensure-tmp
	go mod tidy
	go mod download

lint: ensure-tmp
	staticcheck ./...

test: ensure-tmp
	go test -v -race ./...

# Крос-компіляція для різних платформ
build-linux-amd64: ensure-tmp
	GOOS=linux GOARCH=amd64 go build -o $(APP)-linux-amd64 .
build-linux-arm64: ensure-tmp
	GOOS=linux GOARCH=arm64 go build -o $(APP)-linux-arm64 .
build-darwin-amd64: ensure-tmp
	GOOS=darwin GOARCH=amd64 go build -o $(APP)-darwin-amd64 .
build-darwin-arm64: ensure-tmp
	GOOS=darwin GOARCH=arm64 go build -o $(APP)-darwin-arm64 .
build-windows-amd64: ensure-tmp
	GOOS=windows GOARCH=amd64 go build -o $(APP)-windows-amd64.exe .
build-windows-arm64: ensure-tmp
	GOOS=windows GOARCH=arm64 go build -o $(APP)-windows-arm64.exe .

# Мультиархітектурний Docker buildx
image: ensure-tmp
	docker buildx build --platform $(PLATFORMS) -t $(REGISTRY)/$(APP):$(VERSION) --push .

push: ensure-tmp
	docker push $(REGISTRY)/$(APP):$(VERSION)

clean: ensure-tmp
	rm -rf $(APP)* build/
	docker rmi $(REGISTRY)/$(APP):$(VERSION) || true

docker-build: ensure-tmp
	docker build -t $(APP):latest .

build: deps format ensure-tmp
	GOOS=$(GOOS) GOARCH=$(GOARCH) go build -o $(APP) .

images: ensure-tmp
	docker images | grep smaystr-bot

# --- Simple alias targets required by external CI checks ---
.PHONY: linux arm macos macos-arm windows windows-arm

linux: ensure-tmp build-linux-amd64
arm: ensure-tmp build-linux-arm64
macos: ensure-tmp build-darwin-amd64
macos-arm: ensure-tmp build-darwin-arm64
windows: ensure-tmp build-windows-amd64
windows-arm: ensure-tmp build-windows-arm64