export PATH=/usr/conda/bin:"$PATH"
export DGLBACKEND=pytorch

# python3 -m venv --system-site-packages env;
# unzip models/fine-fine-tuned/mp_gappbe_alignnn.zip -d models/mp_gappbe_alignnn
# source env/bin/activate; python3 -m pip install --no-cache-dir --no-index -f wheels/ -r requirements.txt; python3 generate_submission.py
python3 generate_submission.py