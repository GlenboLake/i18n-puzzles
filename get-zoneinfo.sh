# Download and compile time-zone data for puzzle #19
HOST=https://data.iana.org/time-zones/releases/
VERSION=$1
FILE=tzdb-$VERSION.tar.lz

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

INSTALL_PATH=$SCRIPT_DIR/$VERSION

set -ex

wget $HOST/$FILE
mkdir -p $INSTALL_PATH
tar --lzip -xvf "$FILE"

cd tzdb-$VERSION
make TOPDIR=$INSTALL_PATH install
