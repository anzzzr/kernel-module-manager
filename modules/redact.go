package modules

import (
	"regexp"
)

var (
	// Redact IPv4 addresses (excluding 127.0.0.1 if benign)
	reIPv4 = regexp.MustCompile(`\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b`)

	// Redact standard IEEE 802 MAC addresses (e.g., 00:15:5d:01:02:03 or 00-15-5D-01-02-03)
	reMAC = regexp.MustCompile(`\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b`)

	// Redact hardware serial numbers (e.g., serial=WD-WCC..., serial: ABC123XYZ)
	reSerial = regexp.MustCompile(`(?i)(serial[:=\s]+)[A-Za-z0-9_-]{6,}`)

	// Redact user home directory paths (/home/username/... -> /home/[REDACTED]/...)
	reHomePath = regexp.MustCompile(`/(?:home|Users)/([a-zA-Z0-9._-]+)/`)

	// Redact common auth tokens, API keys, and password patterns
	reSecrets = regexp.MustCompile(`(?i)(token|password|passwd|secret|key|bearer)[:=\s]+[A-Za-z0-9_\-\.]{8,}`)
)

// RedactEvidence sanitizes diagnostic log strings to prevent leaking internal IPs, MACs, usernames, or secrets.
func RedactEvidence(input string) string {
	if input == "" {
		return ""
	}

	// 1. Redact Secrets / Tokens
	res := reSecrets.ReplaceAllString(input, "${1}=[REDACTED_SECRET]")

	// 2. Redact MAC addresses
	res = reMAC.ReplaceAllString(res, "[REDACTED_MAC]")

	// 3. Redact IPv4 addresses (preserving loopback 127.0.0.1 for local service references)
	res = reIPv4.ReplaceAllStringFunc(res, func(ip string) string {
		if ip == "127.0.0.1" || ip == "0.0.0.0" {
			return ip
		}
		return "[REDACTED_IP]"
	})

	// 4. Redact Serial numbers
	res = reSerial.ReplaceAllString(res, "${1}[REDACTED_SERIAL]")

	// 5. Redact usernames in home directory paths
	res = reHomePath.ReplaceAllString(res, "/home/[REDACTED_USER]/")

	return res
}
