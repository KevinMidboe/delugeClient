.PHONY: clean
binaries=dist build

install:
	python3 setup.py install

build:
	python3 setup.py build

dist:
	python3 setup.py sdist

upload: clean dist
	twine upload dist/*

clean:
	rm -rf $(binaries)
