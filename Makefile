APP ?= smaystr-bot
VERSION := $(shell git describe --tags --always || echo "v0.0.0")
REGISTRY ?= smaystr

## Змінні для кросс-компіляції
GOOS ?= linux
GOARCH ?= amd64
TARGETS ?= $(GOOS)-$(GOARCH)
PLATFORMS ?= linux-amd64,linux-arm64

## Налаштування Docker
TAG ?= $(VERSION)
PUSH_IMAGE ?= yes
DOCKER ?= docker

## Налаштування темпорарі директорій
export TMPDIR := $(shell mkdir -p .tmp && chmod -R 777 .tmp && echo "$${PWD}/.tmp")
export TMP := $(TMPDIR)
export TEMP := $(TMPDIR)

## Забезпечує наявність тимчасових директорій
.PHONY: ensure-tmp
ensure-tmp:
	@mkdir -p .tmp tmp /tmp 2>/dev/null || true
	@chmod -R 777 .tmp tmp 2>/dev/null || true
	@echo "Temporary directories prepared: $(TMPDIR)"

## Лістинг існуючих docker образів
.PHONY: images
images:
	@$(DOCKER) images "$(APP)*" --format "{{.Repository}}:{{.Tag}} ({{.ID}}) {{.Size}}"

## Форматування коду
.PHONY: format
format:
	@echo "Formatting code..."
	@gofmt -s -w .

## Залежності
.PHONY: deps
deps:
	@echo "Updating dependencies..."
	@go mod tidy
	@go mod download

## Перевірка коду
.PHONY: lint
lint:
	@echo "Running static checks..."
	@staticcheck ./...

## Тести (з перевіркою race)
.PHONY: test
test: ensure-tmp
	@echo "Running tests..."
	@go test -race ./...

## Білд для поточної платформи
.PHONY: build
build: ensure-tmp
	@echo "Building $(APP)..."
	@CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH) go build -o $(APP)-$(GOOS)-$(GOARCH) -ldflags "-X main.version=$(VERSION)"
	@ln -sf $(APP)-$(GOOS)-$(GOARCH) $(APP)
	@echo "Binary: $(APP)-$(GOOS)-$(GOARCH)"

## Docker образ
.PHONY: image
image: ensure-tmp
	@echo "Building Docker image $(REGISTRY)/$(APP):$(TAG)..."
	@$(DOCKER) build -t $(REGISTRY)/$(APP):$(TAG) .
	@$(DOCKER) tag $(REGISTRY)/$(APP):$(TAG) ghcr.io/$(REGISTRY)/$(APP):$(TAG)
	@echo "Created image: $(REGISTRY)/$(APP):$(TAG)"

## Пуш образу в реєстр
.PHONY: push
push: ensure-tmp
	@echo "Pushing $(REGISTRY)/$(APP):$(TAG) to registry..."
	@$(DOCKER) push ghcr.io/$(REGISTRY)/$(APP):$(TAG)
	@echo "Pushed: ghcr.io/$(REGISTRY)/$(APP):$(TAG)"

## Мультиплатформенний білд через docker buildx
.PHONY: buildx
buildx: ensure-tmp
	@echo "Building multi-platform image for: $(PLATFORMS)..."
	@$(DOCKER) buildx build --platform $(PLATFORMS) -t ghcr.io/$(REGISTRY)/$(APP):$(TAG) --push .
	@echo "Built and pushed multi-platform image: ghcr.io/$(REGISTRY)/$(APP):$(TAG)"

## Очищення артефактів
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@rm -f $(APP)
	@rm -f $(APP)-*
	@rm -rf .tmp tmp

# --- Simple alias targets required by external CI checks ---
.PHONY: linux arm macos macos-arm windows windows-arm

linux: ensure-tmp build-linux-amd64
arm: ensure-tmp build-linux-arm64
macos: ensure-tmp build-darwin-amd64
macos-arm: ensure-tmp build-darwin-arm64
windows: ensure-tmp build-windows-amd64
windows-arm: ensure-tmp build-windows-arm64