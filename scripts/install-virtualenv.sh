echo
echo create chainhammer-substrate virtualenv
echo
echo after possibly removing a whole existing env/ folder !!!
echo 
echo the new virtualenv will be installed below here:
echo $(pwd)
echo 
read -p "Think twice. Then press enter to continue"
echo

set -x
deactivate
rm -rf env 
python3 -m venv env
echo

set +x
echo +++ source env/bin/activate
source env/bin/activate
set -x
echo

# fix specific versions - because otherwise sooooo many problems:
python3 -m pip install pip==20.1.1 wheel==0.34.2
python3 -m pip install -r requirements.txt

: '
# OR ... try new versions - or old on an older system:
source env/bin/activate
python3 -m pip install --upgrade pip wheel
python3 -m pip install --upgrade requests xxhash websockets matplotlib pandas
python3 -m pip install --upgrade ipykernel jupyter pytest pytest-cov 
python3 -m pip install --upgrade scalecodec substrate-interface
'

ipython kernel install --user --name="Python3.substrate"
set +x

echo
