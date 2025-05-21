APP ?= smaystr-bot
REGISTRY ?= quay.io/smaystr
VERSION = $(shell git describe --tags --abbrev=0 2>/dev/null || echo dev)-$(shell git rev-parse --short HEAD)
GOARCH ?= amd64
GOOS ?= linux
PLATFORMS = linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64

format:
	gofmt -s -w ./

deps:
	go mod tidy
	go mod download

lint:
	staticcheck ./...

test:
	go test -v -race ./...

# Крос-компіляція для різних платформ
build-linux-amd64:
	GOOS=linux GOARCH=amd64 go build -o $(APP)-linux-amd64 .
build-linux-arm64:
	GOOS=linux GOARCH=arm64 go build -o $(APP)-linux-arm64 .
build-darwin-amd64:
	GOOS=darwin GOARCH=amd64 go build -o $(APP)-darwin-amd64 .
build-darwin-arm64:
	GOOS=darwin GOARCH=arm64 go build -o $(APP)-darwin-arm64 .
build-windows-amd64:
	GOOS=windows GOARCH=amd64 go build -o $(APP)-windows-amd64.exe .

# Мультиархітектурний Docker buildx
image:
	docker buildx build --platform $(PLATFORMS) -t $(REGISTRY)/$(APP):$(VERSION) --push .

push:
	docker push $(REGISTRY)/$(APP):$(VERSION)

clean:
	rm -rf $(APP)* build/
	docker rmi $(REGISTRY)/$(APP):$(VERSION) || true

docker-build:
	docker build -t $(APP):latest .

build: deps format
	GOOS=$(GOOS) GOARCH=$(GOARCH) go build -o $(APP) .