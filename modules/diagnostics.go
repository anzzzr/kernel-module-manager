package modules

import (
 "context"
 "os/exec"
 "regexp"
 "strings"
 "time"
)

var validModule = regexp.MustCompile(`^[a-zA-Z0-9_][a-zA-Z0-9_-]{0,127}$`)
func ValidModule(name string) bool { return validModule.MatchString(name) }

type Evidence struct {
 Module string `json:"module"`
 Commands map[string]string `json:"commands"`
 Errors map[string]string `json:"errors,omitempty"`
}

func Diagnose(name string) Evidence {
 e := Evidence{Module:name, Commands:map[string]string{}, Errors:map[string]string{}}
 if !ValidModule(name) { e.Errors["validation"] = "invalid module name"; return e }
 for _, spec := range []struct{ key string; args []string }{
  {"uname", []string{"uname", "-r"}},
  {"lsmod", []string{"lsmod"}},
  {"modinfo", []string{"modinfo", name}},
  {"dmesg", []string{"sh", "-c", "dmesg 2>&1 | tail -50"}},
  {"journalctl", []string{"sh", "-c", "journalctl -k --no-pager -n 30 2>&1"}},
  {"modprobe_deps", []string{"modprobe", "--show-depends", name}},
  {"loaded_check", []string{"sh", "-c", "lsmod 2>/dev/null | grep -i " + name}},

 } {
  ctx,cancel := context.WithTimeout(context.Background(), 3*time.Second)
  out,err := exec.CommandContext(ctx,spec.args[0],spec.args[1:]...).CombinedOutput()
  cancel()
  result := strings.TrimSpace(string(out))
  if len(result)>12000 { result=result[:12000]+"...[truncated]" }
  e.Commands[spec.key]=result
  if err!=nil { e.Errors[spec.key]=err.Error() }
 }
 return e
}
