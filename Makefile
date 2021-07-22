fix : 
	autopep8 --in-place src/*.py
	make lint
lint :
	pylint hedgehog/
venv :
	bin/venv.sh
clean : 
	rm -rf venv/
