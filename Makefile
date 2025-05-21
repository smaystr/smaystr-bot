APP ?= smaystr-bot
REGISTRY ?= smaystr
VERSION = $(shell git describe --tags --abbrev=0 2>/dev/null || echo dev)-$(shell git rev-parse --short HEAD)
TARGETOS ?= linux
GOARCH ?= amd64

format:
	gofmt -s -w ./

deps:
	go mod tidy
	go mod download

lint:
	staticcheck ./...

test:
	go test -v -race ./...

build: deps format
	CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${GOARCH} go build -v -o ${APP} -ldflags "-X=github.com/smaystr/smaystr-bot/cmd.appVersion=${VERSION}"

image: build
	docker build -t ${REGISTRY}/${APP}:${VERSION}-${GOARCH} .

push:
	docker push ${REGISTRY}/${APP}:${VERSION}-${GOARCH}

clean:
	rm -rf ${APP} build/

docker-build:
	docker build -t ${APP}:latest .