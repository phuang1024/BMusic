rm -rf ./build
mkdir ./build

cp -r ./bmusic ./build/bmusic

cd ./build
find -name __pycache__ | xargs rm -rf
tar -czvf ./bmusic.tar.gz ./bmusic
