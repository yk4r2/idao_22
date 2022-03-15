# 📈 [International Data Analysis Olympiad](https://idao.world/)
## 👯 Team: NESCafé Gold 3in1

Current python version: 3.9.6\
⚠️ Please add all your tasks to [Google Sheets](https://docs.google.com/spreadsheets/d/1RAPW0PNO2wJscj2wjK-vw9kd-JrSj9u3ZZPUzFGEaw4/edit?usp=sharing) and separate branches.

## 🔗 Useful links
- [Contest](https://official.contest.yandex.ru/contest/34916/problems/)
- [Leaderboard](https://official.contest.yandex.ru/contest/34916/standings/)
- [Colab notebook](https://colab.research.google.com/drive/1NZhOvrt8FKLhnZgiQzNDuF2NApU2E0al?usp=sharing) with [ALIGNN](https://github.com/usnistgov/alignn) fine-tuning and inference.
- [Colab notebook](https://colab.research.google.com/drive/1dSpGZz-TYmOxv9xH2A65kMdPb1XtMEQp?usp=sharing) with ALIGNN inference.
- [Colab notebook](https://colab.research.google.com/drive/1V3cAuli1yd3ZCP7WJ77XBKBSofeodwQ_?usp=sharing) with datasets download scripts (jrom [jarvis](https://github.com/usnistgov/jarvis)), unused in final submission.
- [Big dataset for Track 1 on Kaggle](https://www.kaggle.com/yk4r22/idao-22) with features and predictions for gradient boosting.
- [Notebook for Track 1 on Kaggle](https://www.kaggle.com/yk4r22/idao-tries): stacking ALIGNN and MegNet regressors using self-made graph features by @sunruslan and [jarvis CFID descriptor](https://jarvis-materials-design.github.io/dbdocs/jarvisml/).
- [Downsized dataset for Track 2 on Kaggle](https://jarvis-materials-design.github.io/dbdocs/jarvisml/) with graph features and CFID-descriptors for mixing with MegNet, used for training final model on Track 2.
- [Notebook for Track 2 on Kaggle](https://www.kaggle.com/yk4r22/catboost-track2) for boosting training over MegNet predictions and Track 2 dataset features. For more information about stacking method check the [Track 2 branch](https://github.com/yk4r2/idao_22/tree/final/track2).
- Team credentials are in Telegram.

## 🛠 Installation
- `pyenv` from [here](https://github.com/pyenv/pyenv)
- `poetry`: ```pip install poetry```
- all the needed packages from `pyproject.toml` and your own `venv`:
	- ```pyenv install 3.9.6 && pyenv local 3.9.6```
	- `poetry` instruction can be found [here](https://blog.jayway.com/2019/12/28/pyenv-poetry-saviours-in-the-python-chaos/)
	- ```poetry update```
- you can find the `get_data.sh` script in the `data/` folder: ```cd data/ && /bin/bash get_data.sh```


## 🏗 Structure
- `ad-hoc`: a directory for notebooks and ad-hoc scripts.
	- Contains everybody's sandboxes.
- `scripts`: a directory for models and training scripts.
	- Please create separate branches for any hypothesis you have.

## 🗒 Notes
I added [wemake-python-styleguide](https://wemake-python-stylegui.de/) flake8 plugin and some autoreformatters to dev dependencies. Please use `black` at least.

