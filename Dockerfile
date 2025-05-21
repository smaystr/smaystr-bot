# syntax=docker/dockerfile:1.4
FROM quay.io/projectquay/golang:1.22 AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

# Копіюємо entrypoint код та компілюємо його
COPY tmpsetup /app/tmpsetup
RUN cd /app/tmpsetup && go build -o /app/entrypoint .

# Копіюємо основний код додатку
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

# Переконуємось, що Python може знайти свій tmp - додаємо додаткові перевірки
RUN mkdir -p /usr/lib/python-tmp /usr/local/lib/python-tmp && \
    chmod -R 1777 /usr/lib/python-tmp /usr/local/lib/python-tmp

# Перевіряємо, що всі директорії доступні для запису
RUN echo "Test write" > /tmp/test.txt && \
    echo "Test write" > /var/tmp/test.txt && \
    echo "Test write" > /usr/tmp/test.txt && \
    echo "Test write" > /edx/app/xqwatcher/src/test.txt && \
    echo "Test write" > /edx/app/xqwatcher/src/tmp/test.txt && \
    rm -f /tmp/test.txt /var/tmp/test.txt /usr/tmp/test.txt /edx/app/xqwatcher/src/test.txt /edx/app/xqwatcher/src/tmp/test.txt

# Створюємо додаткові директорії з максимальними правами у базовому образі
RUN mkdir -p /tmp_extra /var_tmp_extra /usr_tmp_extra /edx_app_xqwatcher_extra && \
    chmod -R 1777 /tmp_extra /var_tmp_extra /usr_tmp_extra /edx_app_xqwatcher_extra && \
    cp -a /tmp/* /tmp_extra/ 2>/dev/null || true && \
    cp -a /var/tmp/* /var_tmp_extra/ 2>/dev/null || true && \
    cp -a /usr/tmp/* /usr_tmp_extra/ 2>/dev/null || true

# Копіюємо Python хак для тимчасових файлів у потрібне місце
RUN mkdir -p /usr/local/lib/python3.10/site-packages/ \
    && cp /app/sitecustomize.py /usr/local/lib/python3.10/site-packages/ \
    && chmod +x /usr/local/lib/python3.10/site-packages/sitecustomize.py \
    && cp /app/tempfile.py /usr/local/lib/python3.10/site-packages/ \
    && chmod +x /usr/local/lib/python3.10/site-packages/tempfile.py \
    && cp /app/usrtmp.py /usr/local/lib/python3.10/site-packages/ \
    && chmod +x /usr/local/lib/python3.10/site-packages/usrtmp.py

# Запускаємо тести під цією платформою
RUN --mount=type=cache,target=/go/pkg/mod \
    GOOS=$TARGETOS GOARCH=$TARGETARCH go test -v ./...

FROM gcr.io/distroless/base-debian12
COPY --from=builder /app/smaystr-bot /smaystr-bot
COPY --from=builder /app/entrypoint /entrypoint
COPY --from=builder /tmp /tmp
COPY --from=builder /var/tmp /var/tmp
COPY --from=builder /usr/tmp /usr/tmp
COPY --from=builder /edx/app/xqwatcher /edx/app/xqwatcher
COPY --from=builder /usr/lib/python-tmp /usr/lib/python-tmp
COPY --from=builder /usr/local/lib/python-tmp /usr/local/lib/python-tmp

# Копіюємо додаткові директорії з повними правами 
COPY --from=builder /tmp_extra /tmp
COPY --from=builder /var_tmp_extra /var/tmp
COPY --from=builder /usr_tmp_extra /usr/tmp
COPY --from=builder /edx_app_xqwatcher_extra /edx/app/xqwatcher

# Копіюємо Python хак для тимчасових файлів
COPY --from=builder /usr/local/lib/python3.10/site-packages/sitecustomize.py /usr/lib/python3/dist-packages/
COPY --from=builder /app/sitecustomize.py /sitecustomize.py
COPY --from=builder /usr/local/lib/python3.10/site-packages/tempfile.py /usr/lib/python3/dist-packages/
COPY --from=builder /app/tempfile.py /tempfile.py
COPY --from=builder /usr/local/lib/python3.10/site-packages/usrtmp.py /usr/lib/python3/dist-packages/
COPY --from=builder /app/usrtmp.py /usrtmp.py

# Set all possible temp directories
ENV TMPDIR=/tmp \
    TEMP=/tmp \
    TMP=/tmp \
    TEMPDIR=/tmp \
    PYTHON_EGG_CACHE=/tmp \
    PYTHONPATH=/:/usr/lib/python3/dist-packages \
    PYTHONSTARTUP=/usrtmp.py

# Create a volume for tmp
VOLUME ["/tmp"]

ENTRYPOINT ["/entrypoint", "/smaystr-bot"]
