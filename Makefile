venv: venv/touchfile

venv/touchfile: requirements.txt dev_requirements.txt
	test -d venv || bin/venv.sh
	touch venv/touchfile
fix : venv
	source ./venv/bin/activate;
	autopep8 --in-place src/*.py
	make lint
lint : venv
	source ./venv/bin/activate;
	pylint src/
clean:
	rm -rf venv
	find . | grep ".pyc$$" | xargs rm || true
