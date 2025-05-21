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

# Створюємо і налаштовуємо усі можливі tmp-каталоги з правильними правами доступу
RUN mkdir -p /tmp /var/tmp /usr/tmp && chmod -R 1777 /tmp /var/tmp /usr/tmp

# Create edX directories as well
RUN mkdir -p /edx/app/xqwatcher/src /edx/app/xqwatcher/src/tmp && chmod -R 1777 /edx/app/xqwatcher/src

# Переконуємось, що Python може знайти свій tmp
RUN mkdir -p /usr/lib/python-tmp /usr/local/lib/python-tmp && \
    chmod -R 1777 /usr/lib/python-tmp /usr/local/lib/python-tmp

# Запускаємо тести під цією платформою
RUN --mount=type=cache,target=/go/pkg/mod \
    GOOS=$TARGETOS GOARCH=$TARGETARCH go test -v ./...

FROM gcr.io/distroless/base-debian12
COPY --from=builder /app/smaystr-bot /smaystr-bot
COPY --from=builder /tmp /tmp
COPY --from=builder /var/tmp /var/tmp
COPY --from=builder /usr/tmp /usr/tmp
COPY --from=builder /edx/app/xqwatcher /edx/app/xqwatcher
COPY --from=builder /usr/lib/python-tmp /usr/lib/python-tmp
COPY --from=builder /usr/local/lib/python-tmp /usr/local/lib/python-tmp

# Set all possible temp directories
ENV TMPDIR=/tmp \
    TEMP=/tmp \
    TMP=/tmp \
    TEMPDIR=/tmp \
    PYTHON_EGG_CACHE=/tmp

# Create a volume for tmp
VOLUME ["/tmp"]

ENTRYPOINT ["/smaystr-bot"]
