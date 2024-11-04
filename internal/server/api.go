package server

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/anzzzr/kernel-module-manager/modules"
	"github.com/gorilla/mux"
)

func loadModuleHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	moduleName := vars["module"]

	err := modules.LoadModule(moduleName)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error loading module: %s", err), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]string{
		"message": fmt.Sprintf("Module %s loaded successfully", moduleName),
	})
}

func unloadModuleHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	moduleName := vars["module"]

	err := modules.UnloadModule(moduleName)
	if err != nil {
		http.Error(w, fmt.Sprintf("Error unloading module: %s", err), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]string{
		"message": fmt.Sprintf("Module %s unloaded successfully", moduleName),
	})
}

func InitRouter() *mux.Router {
	router := mux.NewRouter()
	router.HandleFunc("/module/load/{module}", loadModuleHandler).Methods("POST")
	router.HandleFunc("/module/unload/{module}", unloadModuleHandler).Methods("POST")
	return router
}
