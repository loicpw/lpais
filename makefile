all: install

install: 
	pip install -r requirements.txt
	pip install .

dev: 
	pip install -r requirements-dev.txt
	pip install -e .

freeze: 
	pip freeze | sort | grep -v 'lpais'
test: 
	cd tests && ( pytest -rXxs -vv --cov-report html --cov-report term-missing --cov lpais )

doc: 
	cd docs && make html

