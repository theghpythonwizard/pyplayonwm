RED='\033[31m'
YELLOW='\e[33m'
GREEN='\033[32m'
RESET='\e[0m'

base_directory="pyplayonwm"
full_path="pyplayonwm/pyplayonwm"

if [[ $PWD != *"$base_directory" ]]; then
    printf "%b%s%b\n" "$RED" "cd to the top level pyplayonwm before running" "$RESET"
    exit 1
fi

if [[ $PWD == *"$full_path" ]]; then
    printf "%b%s%b\n" "$RED" "cd to the top level pyplayonwm before running" "$RESET"
    exit 1
fi

if [[ -d "$PWD/venv_pyplayon" ]]; then
    printf "%b%s%b\n" "$GREEN" "venv already exists, activating virtual environment"
    source "$PWD/venv_pyplayon/bin/activate"
    printf "%b%s%b\n" "$GREEN"  "venv_directory=$VIRTUAL_ENV" "$RESET"
else
    printf "%b%s%b\n" "$YELLOW" "venv does not exist, creating pyplayon virtual environment" "$RESET"
    python3 -m venv venv_pyplayon
    source "$PWD/venv_pyplayon/bin/activate"
    printf "%b%s%b\n" "$GREEN" "venv_directory=$VIRTUAL_ENV" "$RESET" || printf "%b%s%b\n" "$RED" "venv does not exist" "$RESET"
fi

python -m pip install --upgrade pip
pip install -r requirements.txt

text="Virtual env was setup. run 'source venv_pyplayon/bin/activate' from the top level 'pyplayonwm' directory before use."
printf "%b%s%b\n" "$YELLOW" "$text" "$RESET"