.PHONY: clean
binaries=dist build

install:
	python3 setup.py install

build:
	python3 setup.py build

tarball:
	python3 setup.py sdist

wheel:
	python3 setup.py bdist_wheel

dist: tarball wheel

upload: clean dist
	twine upload dist/*

clean:
	rm -rf $(binaries)
