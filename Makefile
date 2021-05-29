project := httplog

.PHONY: build
build:
	docker build -t $(project) .

.PHONY: install
install:
	pip3 install -e .

.PHONY: test
test:
	python3 -m unittest discover -s tests

.PHONY: dev
dev:
	python3 setup.py develop

