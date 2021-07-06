rm -vrf ./build ./dist  ./*.pyc ./*.tgz ./*.egg-info

./venv/bin/python setup.py sdist
./venv/bin/pip wheel --wheel-dir=./dist ./  --trusted-host pypi.bvrft.cn

#twine upload ./dist/Mask-*.whl