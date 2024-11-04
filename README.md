# Kernel Module Management System (Backend)

## Overview

The **Kernel Module Management System** is a Go-based application that provides an API for managing Linux kernel modules. This system allows users to load and unload kernel modules programmatically through HTTP requests, facilitating easier management without needing direct command-line interaction.

## Features

- Load and unload kernel modules via RESTful API.
- Error handling and status messages for each operation.
- Simple structure for easy expansion and modification.

## Technologies Used

- **Backend Language:** Go
- **Routing:** Gorilla Mux
- **HTTP Server:** Go's built-in `net/http`

## Getting Started

### Prerequisites

- Go (1.16 or later) installed on your system.
- A Linux environment (Ubuntu, Fedora, etc.) for loading and unloading kernel modules.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/kernel-module-manager.git
   cd kernel-module-manager go mod tidy

2. **Build the Application**
   ```bash
   go mod tidy

3. **Run the Application**
   ```bash
   sudo go run main.go
   
4. **API Endpoints**

- Load a Module
- Endpoint: POST /module/load/{module}
- Description: Loads the specified kernel module.
- Example:
```bash
  curl -X POST http://localhost:8080/module/load/loop
