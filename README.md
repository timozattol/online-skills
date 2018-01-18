# EPFL Optional Project 2017 - CHILI Laboratory

Optional Master Project done in the [CHILI Lab](https://chili.epfl.ch/), supervised by Pierre Dillenbourg.

## Abstract
Online educational resources have been developing a lot in the past years and it has become easier to follow distance courses & acquire knowledge whilst sitting in front of a computer. This   project   aimed   at   easing   the   detection   of   current   and upcoming sources of online knowledge by building an automatic tool  for  course  webpage  classification,  using  Machine  Learning techniques.  The  tool  was  provided  with  a  manually  constructed training set of labeled webpages and was then improved with a semi-automatic collection algorithm. Despite the difficulty of the task and the small size of the training set, the tool achieved a final accuracy  of  0.726  for  differentiating  between  online  knowledge and other types of webpages. Finally, potential applications of the tool are presented in the context of online educational resources detection

## Report
The full report is available here.

## Requirements
The project was made in Python using some Data Science libraries such as [scikit-learn](http://scikit-learn.org) and [Pandas](https://pandas.pydata.org/). Other useful libraries such as [NetworkX](https://networkx.github.io/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) were used.

The complete list of requirements lies in [requirements.txt](requirements.txt)

## Run the project
Download the project, install the requirements & run the notebooks. It is adviseable to create a [Virtual Environment](https://docs.python.org/3/library/venv.html) first.

```bash
folder="webpage_classification"
mkdir "$folder"
git clone git@github.com:timozattol/online-skills.git "$folder"
cd "$folder"

pip install -r requirements.txt

jupyter notebook
```

