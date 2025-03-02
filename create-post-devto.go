package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
)

func main() {
	DEVAPIKEY := os.Getenv("DEV_TO_GIT_TOKEN")
	client := &http.Client{}
	var data = strings.NewReader(`{"article":{"title":"Template","body_markdown":"Body","published":false,"tags":["tag1", "tag2"]}}`)
	req, err := http.NewRequest("POST", "https://dev.to/api/articles", data)
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("api-key", DEVAPIKEY)
	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()
	bodyText, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%s\n", bodyText)
}
