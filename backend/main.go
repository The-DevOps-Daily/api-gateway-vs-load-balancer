// A small JSON backend. It counts requests per route so the harness can check
// that every 200 the client saw was served exactly once, and it reports which
// gateway-added headers it received so the transform step can be verified.
package main

import (
	"encoding/json"
	"log"
	"net"
	"net/http"
	"os"
	"strings"
	"sync"
	"sync/atomic"
)

var (
	mu       sync.Mutex
	counts   = map[string]*atomic.Int64{}
	newConns atomic.Int64
)

func counter(route string) *atomic.Int64 {
	mu.Lock()
	defer mu.Unlock()
	c, ok := counts[route]
	if !ok {
		c = &atomic.Int64{}
		counts[route] = c
	}
	return c
}

type reply struct {
	OK      bool   `json:"ok"`
	Route   string `json:"route"`
	Tag     string `json:"tag"`
	APIKey  bool   `json:"api_key_forwarded"`
	Item    string `json:"item"`
	Price   int    `json:"price_cents"`
	Stock   int    `json:"stock"`
	Comment string `json:"comment"`
}

func main() {
	addr := os.Getenv("LISTEN")
	if addr == "" {
		addr = "127.0.0.1:9000"
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/__count", func(w http.ResponseWriter, r *http.Request) {
		out := map[string]int64{}
		mu.Lock()
		for k, v := range counts {
			out[k] = v.Load()
		}
		mu.Unlock()
		// New upstream connections: a proxy that drops keepalive shows up here.
		out["__new_conns"] = newConns.Load()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(out)
	})
	mux.HandleFunc("/__reset", func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		counts = map[string]*atomic.Int64{}
		mu.Unlock()
		newConns.Store(0)
		w.WriteHeader(http.StatusNoContent)
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		route := strings.SplitN(strings.TrimPrefix(r.URL.Path, "/"), "/", 2)[0]
		counter(route).Add(1)
		w.Header().Set("Content-Type", "application/json")
		// The transform step must strip this before it reaches the client.
		w.Header().Set("X-Internal-Debug", "build-7f3a pod=api-2")
		json.NewEncoder(w).Encode(reply{
			OK:      true,
			Route:   route,
			Tag:     r.Header.Get("X-Request-Tag"),
			APIKey:  r.Header.Get("apikey") != "" || r.Header.Get("Authorization") != "",
			Item:    "sku-4411",
			Price:   1299,
			Stock:   37,
			Comment: "a small JSON body, about the size of a typical API read",
		})
	})
	srv := &http.Server{Addr: addr, Handler: mux, ConnState: func(c net.Conn, st http.ConnState) {
		if st == http.StateNew {
			newConns.Add(1)
		}
	}}
	log.Printf("backend listening on %s", addr)
	log.Fatal(srv.ListenAndServe())
}
