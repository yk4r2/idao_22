all: build
build:
	echo "Building"
	bash run.sh
zip:
	bash zip.sh
	