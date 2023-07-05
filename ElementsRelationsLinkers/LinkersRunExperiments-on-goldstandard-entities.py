from Linkers import Linker, SimplerSequenceFlowLinker, SimplerSameGatewayLinker, GatewaysBranchOpener, GatewaysDefaultBranchAdder
from Linkers import FurtherSpecificationLinker
from Linkers import ActivityDataLinker
from Linkers import ActorLinker
from PETAnnotationDataset.AnnotationDataset import AnnotationDataset
import os
from pathlib import Path

curdir = Path(os.path.dirname(os.path.realpath(__file__)))
f=(*curdir.parts[:-2], "LREC_predicted.sopap_dataset.json")
dataset_filename = Path('').joinpath(*f)  
dataset_filename = str(dataset_filename.absolute())
dataset_to_annotate_filename = dataset_filename+'-NEW'

dataset = AnnotationDataset()
dataset.LoadDataset(filename=dataset_filename)

for doc_name in dataset.GetGoldStandardDocuments():
    elements = dataset.GetGoldStandardEntities(doc_name)
    
    linker = Linker()

    #  behavioral linkers
    linker.AddLinker(SimplerSequenceFlowLinker())
    linker.AddLinker(SimplerSameGatewayLinker())
    linker.AddLinker(GatewaysDefaultBranchAdder())
    linker.AddLinker(ActorLinker())
    linker.AddLinker(FurtherSpecificationLinker())
    linker.AddLinker(ActivityDataLinker())
    relations = linker.Parse(elements)
    dataset.AddPredictedRelationsAnnotation(doc_name,
                                            'combinedLiner',
                                            relations)

print('dataset updated?', dataset.SaveDataset(dataset_to_annotate_filename))
