# ==============================================================================
# Go Daemon Dockerfile for kernel-module-manager
#
# SECURITY DIRECTIVE:
# By default, this container runs strictly UNPRIVILEGED as non-root (UID 10001).
# In DEMO_MODE=true, it runs seamlessly on any OS (macOS, Windows, cloud VMs).
#
# To manage real host kernel modules:
#   docker run --cap-add=SYS_MODULE -v /lib/modules:/lib/modules:ro ...
#   (Never require full --privileged unless raw debug access is needed)
# ==============================================================================

# Stage 1: Build binary
FROM golang:1.24-alpine AS builder

WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/kernel-module-manager main.go

# Stage 2: Minimal runtime image
FROM alpine:3.20

# Install kmod utilities (modprobe, rmmod, lsmod, modinfo) and certificates
RUN apk add --no-cache kmod ca-certificates curl

WORKDIR /app

# Copy binary and security policy configuration
COPY --from=builder /out/kernel-module-manager /app/kernel-module-manager
COPY policy.yaml /app/policy.yaml

# Security: Run as unprivileged non-root user by default
RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --retries=5 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/app/kernel-module-manager"]
