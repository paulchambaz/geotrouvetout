build:
	@docker build -t geotrouvetout .

run:
	@docker run --rm -p 8000:8000 -it geotrouvetout /bin/bash

test:
	@tox

lint-file:
	@pydocstyle $(file)
	@pycodestyle --show-source --statistics $(file)
	@mypy --strict --ignore-missing-imports $(file)
	@pylint $(file)

lint-type:
	@mypy --strict --ignore-missing-imports main.py geotrouvetout rest_api tests

lint-doc:
	@pydocstyle main.py geotrouvetout rest_api

lint-lint:
	@pylint main.py geotrouvetout rest_api --exit-zero

lint-style:
	@pycodestyle --show-source --statistics --filename="*.py" main.py geotrouvetout rest_api

lint: lint-type lint-doc lint-style lint-lint

full-test: fmt lint test clean

fmt:
	@black -l 79 geotrouvetout rest_api tests
	
doc:
	@doxygen
	@make -C docs/latex

docker-clean:
	@docker images | awk '$$1 == "geoguessr" { print $$3 }' | xargs -r docker image rm

clean:
	@rm -f .coverage
	@rm -fr .mypy_cache
	@rm -fr .pytest_cache
	@rm -fr .tox
	@find . -name '__pycache__' | xargs rm -fr
	@rm -fr docs/*
	@rm -f poetry.lock

push: build
	@docker tag geotrouvetout:latest paulchambaz/geotrouvetout:latest
	@docker push paulchambaz/geotrouvetout:latest
