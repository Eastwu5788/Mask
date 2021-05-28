#!/usr/bin/env bash
#
# Usage: `sh build.sh` or `sh build.sh -s ./app/protos`
#
scan_dir="./examples"
python_dir="./venv/bin/python"


Help() {
    echo
    echo "Usage: $0 ...[parameters]...
    -h      Show this help message, More: <wudong@eastwu.cn>
    -s      Which path will be scan to find ProtoBuf file, default ${scan_dir}
    -p      Where is your python, default ${python_dir}
    "
}

# getopt 在Mac上体验与Linux存在差异，使用getopts替代
while getopts "hs:,p:" opt;
do
    case $opt in
    h)
        Help; exit 0
    ;;
    s)
       scan_dir=${OPTARG}
    ;;
    p)
       python_dir=${OPTARG}
    ;;
    esac
done


ScanDir() {
    for f in `ls $1`
    do
       if [[ ${f} == "site-packages" ]]; then
           return
       fi

       sub_path="$1/$f"

       if [[ -d ${sub_path} ]]; then
           ScanDir ${sub_path}
       elif [[ ${sub_path} =~ .*proto$ ]]; then
           echo "Start build ${sub_path}"
           ${python_dir} -m grpc_tools.protoc --python_out=${1} --grpc_python_out=${1} -I ${1} ${f}
           name=${f%.proto*}
           sed -i "" "s/import ${name}_pb2 as ${name}__pb2/from . import ${name}_pb2 as ${name}__pb2/" ${1}/${name}_pb2_grpc.py
       fi
    done
}


if [[ ! -d ${scan_dir} ]]; then
    echo "Invalid scan path: ${scan_dir}"
    exit 1
fi

if [[ ! -f ${python_dir} ]]; then
    echo "Invalid python path: ${python_dir}"
fi

ScanDir ${scan_dir}
echo "ProtoBuf file build finished!"
