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
rm -rf env 
python3 -m venv env
echo

set +x
echo +++ source env/bin/activate
source env/bin/activate
set -x
echo

# fix specific versions - because otherwise sooooo many problems:
python3 -m pip install pip==20.0.2 wheel==0.34.2
python3 -m pip install certifi==2019.6.16 idna==2.8 urllib3==1.25.3 # specific demands of substrate-interface==0.9.5
python3 -m pip install requests==2.22.0 xxhash==1.3.0 websockets==8.1 matplotlib==3.2.0 pandas==1.0.1 \
                       ipykernel==5.1.4 jupyter==1.0.0 pytest==5.3.5 pytest-cov==2.8.1 \
                       scalecodec==0.9.17 substrate-interface==0.9.5

ipython kernel install --user --name="Python3.substrate"
set +x

: '
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install --upgrade requests xxhash websockets matplotlib pandas
python3 -m pip install --upgrade ipykernel jupyter pytest pytest-cov 
python3 -m pip install --upgrade scalecodec substrate-interface
'
echo
