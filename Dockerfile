# ---- build stage ----
FROM golang:1.22 AS builder
WORKDIR /app

# Кешуємо залежності
COPY go.mod go.sum ./
RUN go mod download

# Копіюємо решту коду
COPY . .

# Білд через Makefile
RUN make build

# ---- runtime stage ----
FROM gcr.io/distroless/base-debian12
USER nonroot:nonroot
WORKDIR /app
ENV TELE_TOKEN=""
COPY --from=builder /app/smaystr-bot .
ENTRYPOINT ["/app/smaystr-bot"]
