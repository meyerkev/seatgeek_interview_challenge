venv: venv/touchfile

INTERVIEW=seatgeek

venv/touchfile: requirements.txt dev_requirements.txt
	pushd .
	test -d venv || bin/venv.sh
	popd
	touch venv/touchfile
fix : venv
	pwd && source ./venv/bin/activate
	autopep8 --in-place src/*.py
	make lint
lint : venv
	source ./venv/bin/activate;
	pylint src/
clean:
	rm -rf venv
	find . | grep ".pyc$$" | xargs rm || true
docker-pull: FORCE
	docker pull ubuntu:latest
docker-build: FORCE
	docker build -t meyerkev-seatgeek-interview .
up: FORCE # TODO: docker-compose
	docker-compose -f docker-compose.yml -p \
		meyerkev-seatgeek-interview up -d --no-build \
		meyerkev-seatgeek-interview
test: FORCE
	test/seatgeek-be-challenge-linux-amd64
    
# ref: http://www.gnu.org/software/make/manual/html_node/Force-Targets.html#Force-Targets
FORCE:

