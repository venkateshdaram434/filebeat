ARCH?=$(shell uname -m)
GODEP=$(GOPATH)/bin/godep
GOFILES = $(shell find . -type f -name '*.go')

filebeat: $(GOFILES)
	# first make sure we have godep
	go get github.com/tools/godep
	$(GODEP) go build

.PHONY: check
check:
	# This should be modified so it throws an error on the build system in case the output is not empty
	gofmt -d .
	godep go vet ./...

.PHONY: clean
clean:
	gofmt -w .
	-rm filebeat
	-rm filebeat.test
	-rm .filebeat
	-rm profile.cov
	-rm -r coverage

.PHONY: run
run: filebeat
	./filebeat -c etc/filebeat.dev.yml -e -v -d "*"

.PHONY: test
test:
	$(GODEP) go test -short ./...

.PHONY: coverage
coverage:
	# gotestcover is needed to fetch coverage for multiple packages
	go get github.com/pierrre/gotestcover
	mkdir -p coverage
	GOPATH=$(shell $(GODEP) path):$(GOPATH) $(GOPATH)/bin/gotestcover -coverprofile=coverage/unit.cov -covermode=count github.com/elastic/filebeat/...
	$(GODEP) go tool cover -html=coverage/unit.cov -o coverage/unit.html

# Command used by CI Systems
.PHONE: testsuite
testsuite: filebeat
	make coverage

filebeat.test: $(GOFILES)
	$(GODEP) go test -c -cover -covermode=count -coverpkg ./...

full-coverage:
	make coverage
	make -C ./tests/integration coverage
	# Writes count mode on top of file
	echo 'mode: count' > ./coverage/full.cov
	# Collects all integration coverage files and skips top line with mode
	tail -q -n +2 ./coverage/*.cov >> ./coverage/full.cov
	$(GODEP) go tool cover -html=./coverage/full.cov -o coverage/full.html
