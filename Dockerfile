# syntax=docker/dockerfile:1.4
FROM quay.io/projectquay/golang:1.22 AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download
COPY . .

ARG TARGETOS=linux
ARG TARGETARCH=amd64
ARG APP=smaystr-bot

RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /app/$APP .

# Запускаємо тести під цією платформою
RUN --mount=type=cache,target=/go/pkg/mod \
    GOOS=$TARGETOS GOARCH=$TARGETARCH go test -v ./...

FROM scratch
ARG APP=smaystr-bot
COPY --from=builder /app/$APP /$APP

# ---- runtime stage ----
FROM gcr.io/distroless/base-debian12
USER nonroot:nonroot
WORKDIR /app
ENV TELE_TOKEN=""
ENTRYPOINT ["/smaystr-bot"]
