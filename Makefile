SHELL = /bin/bash

venv: venv/touchfile

venv/touchfile: dev_requirements.txt
	test -d venv || bin/venv.sh
	touch venv/touchfile
fix : venv
	. venv/bin/activate
	autopep8 --in-place src/*.py
	make lint
lint : venv
	. ./venv/bin/activate
	pylint src/
clean:
	rm -rf venv
	find . | grep ".pyc$$" | xargs rm || true
docker-pull: FORCE
	docker pull ubuntu:latest
docker-build: FORCE
	docker build --no-cache -t meyerkev-seatgeek-interview .
down: FORCE
	docker-compose -f docker-compose.yml -p \
	    meyerkev-seatgeek-interview stop \
		meyerkev-seatgeek-interview
up: FORCE
	docker-compose -f docker-compose.yml -p \
		meyerkev-seatgeek-interview up -d --no-build \
		meyerkev-seatgeek-interview
sh: FORCE
	docker-compose -f docker-compose.yml -p \
		meyerkev-seatgeek-interview run --rm --service-ports \
		meyerkev-seatgeek-interview /bin/bash
reset: down up
test: reset
	test/seatgeek-be-challenge-linux-amd64
unit-test:
	pytest src/
local: FORCE
	python src/server.py
    
# ref: http://www.gnu.org/software/make/manual/html_node/Force-Targets.html#Force-Targets
FORCE:

