default: all

all:
	python setup.py build

install: all
	python setup.py install

clean:
	rm -f *.pyc
	cd tests && rm -f *.pyc
	cd tbucket && rm -f *.pyc
	cd tests && rm -Rf htmlcov 
	rm -f .coverage tests/.coverage
	rm -f MANIFEST
	rm -Rf build
	rm -Rf dist
	rm -Rf tbucket.egg-info
	rm -Rf tbucket/__pycache__
	rm -Rf tests/__pycache__
	rm -f tests/conf.py
	rm -f tests/auth.txt

sdist: clean
	python setup.py sdist

test:
	flake8 .
	cd tests && nosetests

upload:
	python setup.py sdist register upload

coverage:
	cd tests && coverage run `which nosetests` && coverage html --include='*/tbucket/tbucket/*' --omit='test_*'

coveralls:
	cd tests && nosetests --with-coverage --cover-package=tbucket && ../.coveralls.sh

release: test coverage clean upload clean 
