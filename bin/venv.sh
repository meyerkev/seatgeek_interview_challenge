#/bin/sh

# Make this reasonably agnostic about where it's called from
cd $(dirname $(dirname $0))
venv_dir=venv/

# Turn up and configure the virtualenv
python -m venv ${venv_dir?} 
source ${venv_dir}/bin/activate
pip install -r requirements.txt
