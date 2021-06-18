sudo apt update -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update -y
sudo apt install python3.8 -y
sudo apt install python3.8-venv -y
if [ ! -d "venv-pyplayonwm" ]; then
    python3.8 -m venv venv-pyplayonwm
else
    echo "venv-pyplayonwm already exists"
fi
source venv-pyplayonwm/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

