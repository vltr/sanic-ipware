help:
	@echo "clean - let this project be near mint"
	@echo "black - format the source code with black"
	@echo "requirements-dev - install all required tools for development"

.PHONY: help

black:
	black ./src/middle_schema/ ./tests setup.py

cleanpycache:
	find . -type d | grep "__pycache__" | xargs rm -rf

clean: cleanpycache
	rm -rf ./.coverage
	rm -rf ./.pytest_cache
	rm -rf ./.tox
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./htmlcov
	rm -rf ./src/*.egg-info

requirements-dev:
	pip install pip-tools
	pip-compile -U -r requirements-dev.in --output-file requirements-dev.txt
	pip-compile -U -r
	pip-sync requirements-dev.txt requirements.txt

# release:
# 	tox -e check
# 	python setup.py clean --all sdist bdist
# 	twine upload --skip-existing dist/*.whl dist/*.gz dist/*.zip
