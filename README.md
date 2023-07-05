# PET Dataset Baselines


<center>
Patrizio Bellan, Chiara Ghidini, Mauro Dragoni, Han van der Aa, Simone Paolo Ponzetto

<center>
Fondazione Bruno Kessler, Trento (Italy)
University of Mannheim, Mannheim (Germany)  

**Abstract**. *Process extraction from text is an important task of process discovery, for which various approaches have been developed in recent years. However, in contrast to other information extraction tasks, there is a lack of gold-standard corpora of business process descriptions that are carefully annotated with all the entities and relationships of interest. Due to this, it is currently hard to compare the results obtained by extraction approaches in an objective manner, whereas the lack of annotated texts also prevents the application of data-driven information extraction methodologies, typical of the natural language processing field. Therefore, to bridge this gap, we present the PET dataset, a first corpus of business process descriptions annotated with activities, gateways, actors, and flow information. We present our new resource, including a variety of baselines to benchmark the difficulty and challenges of business process extraction from text. PET can be accessed via  [huggingface.co/datasets/patriziobellan/PET](https://pdi.fbk.eu/pet-dataset/huggingface.co/datasets/patriziobellan/PET)*

### This repository provides the annotations, the gold standard data, and the baselines predictions of the PET dataset

The folder *crf Models* contains the trained crf model used to create *Baseline 1*
The folder *baseline scripts* contains the scripts used to create the three baselines. 
The file *petdatasetgoldstandardbaselines.json* contains the gold standard annotations of the PET dataset and the predictions of the three baselines.

## Visualizers

You can find a python package to see the goldstandard annotations and baselines predictions [here](https://pypi.org/project/PETGoldstandardBaselinesVisualizers/1.0.2/).
You can install it via pip.
```python
pip install PETGoldstandardBaselinesVisualizers==1.0.2
```
  The package provides two visualizers: 
  - BaselinePredictorAgreement, and 
  - BaselineComparisonLineview
  
#### Baseline Predictor Agreement Interface  
  
This visualizer shows the agreement between the baseline predictors and the goldstandard annotations.  
  
```python  
from Visualizers.BaselinePredictorAgreementInterface import Show as agreements  
agreements()  
```  
  
#### Baselines Comparison LineView 
  
This visualizer provides a GUI to compare the goldstandard process element annotations and the Baseline 1 ones.  
  
```python  
from Visualizers.BaselinesComparisonLineView import Show as lineview  
lineview()  
```
## Dataset Data
[PET dataset repository](https://huggingface.co/datasets/patriziobellan/PET)
([Inception](https://inception-project.github.io/)) [Annotation Schema](https://pdi.fbk.eu/pet/inception-schema.json)
[Guidelines](https://pdi.fbk.eu/pet/annotation-guidelines-for-process-description.pdf)

## Cite the dataset

PET Dataset
```
 @inproceedings{DBLP:conf/bpm/BellanADGP22,
  author       = {Patrizio Bellan and
                  Han van der Aa and
                  Mauro Dragoni and
                  Chiara Ghidini and
                  Simone Paolo Ponzetto},
  editor       = {Cristina Cabanillas and
                  Niels Frederik Garmann{-}Johnsen and
                  Agnes Koschmider},
  title        = {{PET:} An Annotated Dataset for Process Extraction from Natural Language
                  Text Tasks},
  booktitle    = {Business Process Management Workshops - {BPM} 2022 International Workshops,
                  M{\"{u}}nster, Germany, September 11-16, 2022, Revised Selected
                  Papers},
  series       = {Lecture Notes in Business Information Processing},
  volume       = {460},
  pages        = {315--321},
  publisher    = {Springer},
  year         = {2022},
  url          = {https://doi.org/10.1007/978-3-031-25383-6\_23},
  doi          = {10.1007/978-3-031-25383-6\_23},
  timestamp    = {Tue, 14 Feb 2023 09:47:10 +0100},
  biburl       = {https://dblp.org/rec/conf/bpm/BellanADGP22.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```

Guidelines

```
> @inproceedings{DBLP:conf/aiia/BellanGDPA22,
  author       = {Patrizio Bellan and
                  Chiara Ghidini and
                  Mauro Dragoni and
                  Simone Paolo Ponzetto and
                  Han van der Aa},
  editor       = {Debora Nozza and
                  Lucia C. Passaro and
                  Marco Polignano},
  title        = {Process Extraction from Natural Language Text: the {PET} Dataset and
                  Annotation Guidelines},
  booktitle    = {Proceedings of the Sixth Workshop on Natural Language for Artificial
                  Intelligence {(NL4AI} 2022) co-located with 21th International Conference
                  of the Italian Association for Artificial Intelligence (AI*IA 2022),
                  Udine, November 30th, 2022},
  series       = {{CEUR} Workshop Proceedings},
  volume       = {3287},
  pages        = {177--191},
  publisher    = {CEUR-WS.org},
  year         = {2022},
  url          = {https://ceur-ws.org/Vol-3287/paper18.pdf},
  timestamp    = {Fri, 10 Mar 2023 16:23:01 +0100},
  biburl       = {https://dblp.org/rec/conf/aiia/BellanGDPA22.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```
