package modules
import "testing"
func TestValidModule(t *testing.T) {
 for _,s:=range []string{"loop","nvidia_uvm","vhost-net"} {if !ValidModule(s) {t.Errorf("expected valid %q",s)}}
 for _,s:=range []string{"","../x",";reboot","a b","-bad"} {if ValidModule(s) {t.Errorf("expected invalid %q",s)}}
}
