import tkinter as tk
import sys
import tkinter.filedialog
from random import seed
# from goldstandardbaselines.src.Predictors.ProcessElementsTaggers.SklearnCRFEstimatorTEST import sklearncrfestimatortest
import numpy as np

from SklearnCRFEstimator2 import sklearncrfestimator
from DataLoaderProcessElements import DataLoader
from pathlib import Path
from PETAnnotationDataset.AnnotationDataset import AnnotationDataset
from CalculateBaselinePredictorsAgreement import CalculateBaselinePredictorsF1

class GoldStandardBaselines(tk.Frame):
    seed(23)
    PE_LIST = ['Activity',
              'Activity Data',
              'Actor',
              'Condition Specification',
              'Further Specification',
              'XOR Gateway',
              'AND Gateway']

    def __init__(self,
                 parent,
                 # dataset=None
                 ):
        tk.Frame.__init__(self, parent)
        self.__init_variables__()

        self.parent = parent
        self.parent.geometry('850x350')
        self.parent.title('Generate GoldStandard Annotations')
        self.dataset = AnnotationDataset()

        self.CreateFrame()


    def __init_variables__(self):
        self.opt_model_type = tk.StringVar()
        self.estimator = None
        self.perform_cross_validation = tk.BooleanVar()
        self.perform_cross_validation.set(True)
        self.model_name = tk.StringVar()

    def CreateFrame(self):

        self.later_frame = tk.Frame(self.parent)
        self.later_frame.pack(side='left',
                              fill='x',
                              expand=True)
        #  model type
        frm_model_type = tk.LabelFrame(self.later_frame,
                                       text='Select Estimator')
        frm_model_type.pack()
        tk.Radiobutton(frm_model_type,
                       text='sklearn PYCRFSUITE',
                       value='pycrfsuite',
                       variable=self.opt_model_type,
                       anchor='nw'
                       ).pack(side='top',
                              anchor='nw',
                              fill='x')

        tk.Radiobutton(frm_model_type,
                       text='ALLEN CRF',
                       value='ALLEN CRF',
                       variable=self.opt_model_type,
                       anchor='nw'
                       ).pack(side='top',
                              anchor='nw',
                              fill='x')
        tk.Entry(frm_model_type,
                 textvariable=self.model_name).pack(side='top',
                                                    fill='x',
                                                    expand=True)

        self.opt_model_type.set('pycrfsuite')
        tk.Button(frm_model_type,
                  text='Train and Test Estimator',
                  command=self.TrainEstimator).pack(side='top',
                                                            fill='x',
                                                            anchor='nw')

        # tk.Button(frm_model_type,
        #           text='Load Estimator',
        #           command=self.LoadEstimator).pack(side='top',
        #                                                     fill='x',
        #                                                     anchor='nw')
        # tk.Checkbutton(frm_model_type,
        #                text='Cross Validation',
        #                variable=self.perform_cross_validation,
        #               # command=self.CrossValidation
        #                ).pack(side='top',
        #                        fill='x',
        #                        anchor='nw')

        frm_load_data = tk.Frame(self.later_frame)
        frm_load_data.pack()
        tk.Button(frm_load_data,
                  text='Load Data',
                  command=self.LoadData).pack()

        tk.Button(frm_load_data,
                  text='Load Dataset to update',
                  command=self.LoadDatasetToUpdate).pack(side='top',
                                                         fill='x',
                                                         anchor='nw')
        tk.Button(frm_load_data,
                  text='Save Results',
                  command=self.SaveResults).pack(side='top',
                                                 fill='x',
                                                 anchor='nw')
        self.frm_body = tk.Frame(self.parent)
        self.frm_body.pack(side='top',
                           fill='both',
                           expand=True)

        frm_log_text = tk.Frame(self.frm_body)
        frm_log_text.pack(expand=True)
        self.ent_log_text = tk.Text(frm_log_text,
                                    height=21,
                                    width=80,
                                    bg='green',
                                    fg='black',
                                     )
        self.ent_log_text.pack(side='left',
                               fill='both',
                               expand=True)
        sb = tk.Scrollbar(frm_log_text, orient='vertical')
        sb.pack(side='left', fill='y')
        self.ent_log_text.config(yscrollcommand=sb.set)
        sb.config(command=self.ent_log_text.yview)

    def TrainEstimator(self):
        #  select estimator type

        # self.current_model_filename = 'conll2002-esp.crfsuite'

        if self.opt_model_type.get() == 'pycrfsuite':
            save_model_path = Path(tkinter.filedialog.askdirectory())
            self.ClearMsgBox()
            self.estimator = sklearncrfestimator()
            self.WriteMessage('\n====TRAINING=====\n')
            results = self.estimator.CrossValidation(self.dataloader.training_dataset,
                                                     self.dataloader.testing_dataset,
                                                     save_model_path)
            #  get results
            training_folds, testing_folds = self.dataloader.convert_predictions_into_doc_predictions(results)

            training_scores = list()
            tesitng_scores = list()
            msg = ''
            #  calculate scores
            for n_fold, training_fold in enumerate(training_folds):
                training_documents_list = training_fold.keys()
                #  add experiment to dataset
                for doc_name in training_documents_list:
                    self.dataset.AddPredictedTokenAnnotation(document_name=doc_name,
                                                             annotator_name=self.model_name.get(),
                                                             entities=training_fold[doc_name]
                                                             )

                agreement = CalculateBaselinePredictorsF1(dataset=self.dataset,
                                                          document_list=list(training_documents_list),
                                                          annotator_name=self.model_name.get(),
                                                          process_elements_list=self.PE_LIST
                                                          )
                f1_score = agreement.ComputeAgreement_pe()
                training_scores.append(f1_score)
                msg = msg + 'training fold : {} - f1 : {}\n'.format(str(n_fold), str(f1_score))
            msg = msg + '\ntraining average f1 : {}\n\n'.format(str(np.average(training_scores)))

            for n_fold, testing_fold in enumerate(testing_folds):
                testing_documents_list = testing_fold.keys()
                #  add experiment to dataset
                for doc_name in testing_documents_list:
                    self.dataset.AddPredictedTokenAnnotation(document_name=doc_name,
                                                             annotator_name=self.model_name.get(),
                                                             entities=testing_fold[doc_name]
                                                             )

                agreement = CalculateBaselinePredictorsF1(dataset=self.dataset,
                                                          document_list=list(testing_documents_list),
                                                          annotator_name=self.model_name.get(),
                                                          process_elements_list=self.PE_LIST
                                                          )
                f1_score = agreement.ComputeAgreement_pe()
                tesitng_scores.append(f1_score)
                msg = msg + 'testing fold : {} - f1 : {}\n'.format(str(n_fold), str(f1_score))
            msg = msg + '\ntesting average f1 : {}\n'.format(str(np.average(tesitng_scores)))
            self.WriteMessage(msg)
            # self.register_experiment(results)

        else:
            self.estimator = None
    #
    # def register_experiment(self,
    #                         results):
    #     # results is {doc_name: [entities -> Activity: [n_sent] = [activities ranges]}
    #
    #     annotator_name = self.model_name.get()
    #     for doc_name in results:
    #         self.dataset.AddPredictedTokenAnnotation(document_name=doc_name,
    #                                                  annotator_name=annotator_name,
    #                                                  entities=results[doc_name])

    def LoadData(self):
        filename = Path(tkinter.filedialog.askdirectory(message='select folder data'))
        if filename:
            self.dataloader = DataLoader(filename)
        print('data loaded')

    def SaveResults(self):
        filename = Path(tk.filedialog.askopenfilename())
        self.dataset.SaveDataset(filename=filename)
        print('dataset updadated')

    # def LoadEstimator(self):
    #     pass

    def LoadDatasetToUpdate(self):
        filename = Path(tk.filedialog.askopenfilename())
        if filename:
            self.dataset.LoadDataset(filename=str(filename))
  
    def WriteMessage(self, msg):
        self.ent_log_text.insert('end', msg)

    def ClearMsgBox(self):
        try:
            self.ent_log_text.delete(0, 'end')
        except:
            pass


if __name__  == '__main__':
    app = tk.Tk()
    program = GoldStandardBaselines(app)
    program.mainloop()
    sys.exit()