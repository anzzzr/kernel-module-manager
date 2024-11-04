package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/anzzzr/kernel-module-manager/internal/server"
)

func main() {
	fmt.Println("Starting Kernel Module Manager API Server...")

	router := server.InitRouter()
	log.Fatal(http.ListenAndServe(":8080", router))
}
