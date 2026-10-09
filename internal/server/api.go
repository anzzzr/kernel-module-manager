package server

import (
 "bytes"
 "encoding/json"
 "fmt"
 "io"
 "net/http"
 "os"
 "strings"
 "time"

 "github.com/anzzzr/kernel-module-manager/modules"
 "github.com/gorilla/mux"
)

func writeJSON(w http.ResponseWriter, code int, v any) { w.Header().Set("Content-Type","application/json"); w.WriteHeader(code); _=json.NewEncoder(w).Encode(v) }
func authorize(w http.ResponseWriter,r *http.Request) bool {
 token:=os.Getenv("MODULE_API_TOKEN")
 if token=="" { writeJSON(w,503,map[string]string{"error":"MODULE_API_TOKEN must be configured"});return false }
 if r.Header.Get("Authorization")!="Bearer "+token {writeJSON(w,401,map[string]string{"error":"unauthorized"});return false}
 return true
}
func loadModuleHandler(w http.ResponseWriter,r *http.Request) {
 if !authorize(w,r) {return}; name:=mux.Vars(r)["module"]
 if !modules.ValidModule(name) {writeJSON(w,400,map[string]string{"error":"invalid module name"});return}
 if err:=modules.LoadModule(name);err!=nil {writeJSON(w,500,map[string]string{"error":err.Error()});return}
 writeJSON(w,200,map[string]string{"message":fmt.Sprintf("Module %s loaded",name)})
}
func unloadModuleHandler(w http.ResponseWriter,r *http.Request) {
 if !authorize(w,r) {return};name:=mux.Vars(r)["module"]
 if !modules.ValidModule(name) {writeJSON(w,400,map[string]string{"error":"invalid module name"});return}
 if err:=modules.UnloadModule(name);err!=nil {writeJSON(w,500,map[string]string{"error":err.Error()});return}
 writeJSON(w,200,map[string]string{"message":fmt.Sprintf("Module %s unloaded",name)})
}
func diagnoseHandler(w http.ResponseWriter,r *http.Request) {
 if !authorize(w,r) {return}; name:=mux.Vars(r)["module"]
 if !modules.ValidModule(name) {writeJSON(w,400,map[string]string{"error":"invalid module name"});return}
 evidence:=modules.Diagnose(name)
 payload,_:=json.Marshal(evidence)
 url:=strings.TrimRight(os.Getenv("AI_SERVICE_URL"),"/")
 if url=="" {writeJSON(w,200,map[string]any{"evidence":evidence,"note":"AI_SERVICE_URL not configured"});return}
 client:=&http.Client{Timeout:35*time.Second}
 req,err:=http.NewRequestWithContext(r.Context(),"POST",url+"/analyze",bytes.NewReader(payload))
 if err!=nil {writeJSON(w,500,map[string]string{"error":err.Error()});return}
 req.Header.Set("Content-Type","application/json")
 if key:=os.Getenv("AI_SERVICE_TOKEN");key!="" {req.Header.Set("Authorization","Bearer "+key)}
 resp,err:=client.Do(req)
 if err!=nil {writeJSON(w,502,map[string]any{"evidence":evidence,"error":"AI service unavailable"});return}
 defer resp.Body.Close()
 body,err:=io.ReadAll(io.LimitReader(resp.Body,100000))
 if err!=nil {writeJSON(w,502,map[string]string{"error":"invalid AI response"});return}
 w.Header().Set("Content-Type","application/json");w.WriteHeader(resp.StatusCode);_,_=w.Write(body)
}
func InitRouter() *mux.Router {
 router:=mux.NewRouter()
 router.HandleFunc("/module/load/{module}",loadModuleHandler).Methods("POST")
 router.HandleFunc("/module/unload/{module}",unloadModuleHandler).Methods("POST")
 router.HandleFunc("/module/{module}/diagnose",diagnoseHandler).Methods("POST")
 router.HandleFunc("/health",func(w http.ResponseWriter,r *http.Request){writeJSON(w,200,map[string]string{"status":"ok"})}).Methods("GET")
 return router
}
