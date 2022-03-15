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

## 🥋 Task
### IDAO 2022 Track 1
![grid img](https://github.com/yk4r2/idao_22/tree/master/images/markdown-image.png)

Two-dimensional transition metal dichalcogenides (TMDCs) are relatively new types of materials that have remarkable properties ranging from semiconducting, metallic, magnetic, superconducting to optical. The chemical composition of TMDCs is MX₂; where M is the group of transition elements most popular Molybdenum and Tungsten, and X is usually Sulfur or Selenium. Atomically thin TMDCs usually contain various defects, which enrich the lattice structure and give rise to many intriguing properties. Engineered point defects in two-dimensional (2D) materials offer an attractive platform for solid-state devices that exploit tailored optoelectronic, quantum emission, and resistive properties. Naturally occurring defects are also unavoidably important contributors to material properties and performance. The immense variety and complexity of possible defects make it challenging to experimentally control, probe, or understand atomic-scale defect-property relationships. In the figure above you can find vacancy and substitution defects in an 8x8 MoS₂ crystal lattice.

Band gap is one of the important physical attributes which describe certain characteristics of the material, that helps deriving material qualities including electric conductivity or catalytic power or photo-optical properties. Band gap is the energy difference between the valence band and conduction band and is closely related to the energy difference between highest occupied molecular orbital (HOMO) and lowest unoccupied molecular orbital (LUMO), materials with overlapping (between valence band and conduction band) or very small band gap are conductors and materials with small bandgap are semiconductors while materials with large bandgap are insulators.

**The task is to predict band gap energy for each crystal structure.**

#### Input format

Training dataset is in the `data` directory in the baseline and structured into a directory called `structures` containing 2967 crystal structures as a json file named with a unique identifier and is containing a special pymatgen structure (check pymatgen documentation for [reference](https://pymatgen.org/index.html)), that contains information about crystal parameters, cartesian coordinates of each atom, atom types, and other information.

The targets are stored in a csv file named `targets.csv` containing two columns; the first is the unique identifier of the structure and the other is the band gap value for each structure. The train and test sets are constructed by sampling the corresponding subset without replacement.

The training sample contains 1796 examples.

The public test sample contains 1484 examples.

The private test sample contains 1483 examples.

#### Output format

Please upload your predictions into the system in the .csv format. The ﬁle should contain two columns: **id, predictions**

A sample submission can be found on [GitHub](https://github.com/HSE-LAMBDA/IDAO-2022).

##### Quality Metric

Energy within Threshold (EwT) is designed to measure the practical usefulness of a model for replacing [DFT](https://en.wikipedia.org/wiki/Density_functional_theory) by evaluating whether the predicted energy is close to the ground truth (DFT energy). EwT is defined as the fraction of structures in which the predicted energy is within `0.02 eV` ([electronvolt](https://en.wikipedia.org/wiki/Electronvolt)) of the ground truth energy.

##### Baseline

The baseline is based on [MEGNet](https://arxiv.org/pdf/1812.05055.pdf), a message passing graph neural network designed for materials by incorporating the natural symmetries in crystals such as rotation invariance, and periodic boundary conditions (PBC). In the reference baseline MEGNet is trained on the dataset.

DFT is not allowed; and, its use will disqualify the modeling solution from the competition.

##### Notes

You may use additional information, data, and advice at your own risk. All solutions will be checked by the jury to guarantee fair play. Please ask us in any vague or unclear case. If you face any problems or have questions, please contact us via e-mail: [hello@idao.world](mailto:hello@idao.world).

##### References

- [Chen, C., Ye, W., Zuo, Y., Zheng, C. and Ong, S.P., 2019. Graph networks as a universal machine learning framework for molecules and crystals. Chemistry of Materials, 31(9), pp.3564-3572.](https://arxiv.org/pdf/1812.05055.pdf)
- [Hu, Z., Wu, Z., Han, C., He, J., Ni, Z. and Chen, W., 2018. Two-dimensional transition metal dichalcogenides: interface and defect engineering. Chemical Society Reviews, 47(9), pp.3100-3128.](https://ir.nsfc.gov.cn//paperDownload/ZD5437990.pdf)
- [Manzeli, S., Ovchinnikov, D., Pasquier, D., Yazyev, O.V. and Kis, A., 2017. 2D transition metal dichalcogenides. Nature Reviews Materials, 2(8), pp.1-15.](https://www.nature.com/articles/natrevmats201733)

