# syntax=docker/dockerfile:1.4
FROM quay.io/projectquay/golang:1.22 AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download
COPY . .

ARG TARGETOS=linux
ARG TARGETARCH=amd64
ARG APP=smaystr-bot

RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /app/$APP .
RUN ls -l /app

# Ensure a world-writable tmp dir that will be copied to the runtime image.
RUN mkdir -p /tmp && chmod 1777 /tmp

# Запускаємо тести під цією платформою
RUN --mount=type=cache,target=/go/pkg/mod \
    GOOS=$TARGETOS GOARCH=$TARGETARCH go test -v ./...

FROM gcr.io/distroless/base-debian12
COPY --from=builder /app/smaystr-bot /smaystr-bot
COPY --from=builder /tmp /tmp
ENV TMPDIR=/tmp
ENTRYPOINT ["/smaystr-bot"]
