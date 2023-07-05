#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 13:56:31 2021

@author: patrizio
print(self.agreement_table.shape)"""

from copy import deepcopy
from itertools import combinations  # used to create annotators pairs
from random import choice, seed
from collections import defaultdict

MAX_ROUND = 3

class CalculateBaselinePredictorsF1:
    pe_labels = ['Activity Data', 'Actor', 'Activity', 'Further Specification',
                 'AND Gateway', 'XOR Gateway', 'Condition Specification']
    re_labels = ['a4Flows',  # Sequence Flow',
                 'a2Uses',  # 'Uses',
                 'Actor Performer',  # 'Roles'
                 'Actor Recipient',  # 'Roles',
                 'a5FurtherSpecification',
                 'a6SameGateway',
                 # 'CorefActor',
                 # 'Coref'  # act data
                 # 'Actor.Coref Activity Data', 'Actor.Coref Mention'
                 ]

    def __init__(self, 
                 dataset,
                 document_list,
                 annotator_name,
                 process_elements_list=None,
                 relations_list=None,
                 ):
        seed(23)

        self.dataset = dataset
        self.document_list = document_list
        self.annotator_name = annotator_name

        self.selected_pe = process_elements_list or self.pe_labels # if process_element_list is none, get all the pe
        self.selected_re = relations_list or self.re_labels  # if process_element_list is none, get all the pe

    def ComputeAgreement(self):
        return self.ComputeAgreement_pe(), self.ComputeAgreement_re()

    def ComputeAgreement_re(self):
        self.CollectTP_FP_FN_re()
        self.precision_re, self.recall_re, self.F1_re, self.support_re = self.Compute_PR_REC_F1_selection_re()
        return self.F1_re

    def ComputeAgreement_pe(self):
        self.CollectTP_FP_FN_pe()
        self.precision_pe, self.recall_pe, self.F1_pe, self.support_pe = self.Compute_PR_REC_F1_selection_pe()
        return self.F1_pe

    def CollectTP_FP_FN_pe(self):
        """
        
#         TP = 0 # oracle and classifier agree
#         FP = 0 # The classifier annotated something that the oracle didn't
#         TN = 0 # I will never have this 
#         FN = 0 # The classifier Missed the annotation
        
        """
        #
        # self.TPs_pe = defaultdict(list)
        # self.FPs_pe = defaultdict(list)
        # self.FNs_pe = defaultdict(list)

        self.TPs_pe = {doc_name:  defaultdict(list) for doc_name in self.document_list}
        self.FPs_pe = {doc_name:  defaultdict(list) for doc_name in self.document_list}
        self.FNs_pe = {doc_name:  defaultdict(list) for doc_name in self.document_list}

        for doc_name in self.document_list:
            for pe_label in self.selected_pe:
                oracle_annotations = deepcopy(self.dataset.dataset['documents'][doc_name]['Gold Standard']['entities'][pe_label])
                classifier_annotations = deepcopy(self.dataset.dataset['documents'][doc_name]['predictors'][self.annotator_name]['entities'][pe_label])
                for n_sent in range(len(oracle_annotations)):
                    if len(oracle_annotations[n_sent]) == 0:
                        # this means that the oracle did not annotated anything in this sentence
                        # il classifier ha annotato qualcosa ma non l'oracolo
                        self.FPs_pe[doc_name][pe_label].append(len(classifier_annotations[n_sent]))
                        continue

                    if len(classifier_annotations[n_sent]) == 0:
                        #classifier has no annotations.
                        # in this case the classifier misses all the oracle annotations
                        self.FNs_pe[doc_name][pe_label].append(len(oracle_annotations[n_sent]))
                        continue
                    # if i am here, there is at least an annotation
                    # loop over annotation ranges
                    for oracle_annotation in oracle_annotations[n_sent]:

                        if self.CheckMatch_pe(oracle_annotation, classifier_annotations[n_sent]):
                            # there is a True Positive
                            self.TPs_pe[doc_name][pe_label].append(1)
                        else:
                            # no match is found, so it is a False Negative
                            self.FNs_pe[doc_name][pe_label].append(1)

    def CheckMatch_pe(self,
                      oracle_annotation,
                      classifier_ranges):
        for classifier_range in classifier_ranges:
            if classifier_range == oracle_annotation:
                #  match found
                #  remove the annotation from classifier
                classifier_ranges.pop(classifier_ranges.index(classifier_range))
                return True
        return False

    def TransformRelationsDict(self, annotations):
        transformed_dict = defaultdict(list)
        for source in annotations:
            for relation in annotations[source]:
                rel_type, target = relation
                transformed_dict[rel_type].append([source, target])
        return transformed_dict

    def CollectTP_FP_FN_re(self):
            """

    #         TP = 0 # oracle and classifier agree
    #         FP = 0 # The classifier annotated something that the oracle didn't
    #         TN = 0 # I will never have this
    #         FN = 0 # The classifier Missed the annotation

            """
            self.TPs_re = {doc_name: defaultdict(list) for doc_name in self.document_list}
            self.FPs_re = {doc_name: defaultdict(list) for doc_name in self.document_list}
            self.FNs_re = {doc_name: defaultdict(list) for doc_name in self.document_list}

            for doc_name in self.document_list:
                oracle_annotations = deepcopy(
                    self.dataset.dataset['documents'][doc_name]['Gold Standard']['relations'])
                classifier_annotations = deepcopy(
                    self.dataset.dataset['documents'][doc_name]['predictors'][self.annotator_name]['relations'])

                oracle_annotations = self.TransformRelationsDict(oracle_annotations)
                classifier_annotations = self.TransformRelationsDict(classifier_annotations)

                #  check matches
                for re_label in self.selected_re:
                    if len(oracle_annotations[re_label]) == 0:
                        # this means that the oracle did not annotated anything in this sentence
                        # il classifier ha annotato qualcosa ma non l'oracolo
                        self.FPs_re[doc_name][re_label].append(len(classifier_annotations[re_label]))
                        continue
                    if len(classifier_annotations[re_label]) == 0:
                            # classifier has no annotations.
                            # in this case the classifier misses all the oracle annotations
                            self.FNs_re[doc_name][re_label].append(len(oracle_annotations[re_label]))
                            continue
                    # if i am here, there is at least an annotation
                    # loop over annotation ranges
                    for oracle_annotation in oracle_annotations[re_label]:
                            if self.CheckMatch_re(oracle_annotation, classifier_annotations[re_label], re_label):
                                # there is a True Positive
                                self.TPs_re[doc_name][re_label].append(1)
                            else:
                                # no match is found, so it is a False Negative
                                self.FNs_re[doc_name][re_label].append(1)

    def CheckMatch_re(self,
                      oracle_annotation,
                      classifier_ranges,
                      re_label):

        for classifier_range in classifier_ranges:
            if re_label == 'a6SameGateway':
                #  direction does not matter
                # print() # classifier_range = [classifier_range[1], classifier_range[0]]
                # if classifier_range[0] == oracle_annotation:
                if classifier_range[0] in oracle_annotation and classifier_range[1] in oracle_annotation:
                    classifier_ranges.pop(classifier_ranges.index(classifier_range))
                    return True
            elif classifier_range == oracle_annotation:
                #  match found
                #  remove the annotation from classifier
                classifier_ranges.pop(classifier_ranges.index(classifier_range))
                return True
        return False
         
# =============================================================================
#   elabora dati per calcolare F1
# =============================================================================
    def Compute_PR_REC_F1_selection_pe(self):
        TP = sum([x
                  for doc_name in self.TPs_pe
                  for pe in self.TPs_pe[doc_name]
                  for x in self.TPs_pe[doc_name][pe]])
        FP = sum([x
                  for doc_name in self.FPs_pe
                  for pe in self.FPs_pe[doc_name]
                  for x in self.FPs_pe[doc_name][pe]])
        FN = sum([x
                  for doc_name in self.FNs_pe
                  for pe in self.FNs_pe[doc_name]
                  for x in self.FNs_pe[doc_name][pe]])
        return self.Compute_PR_REC_F1(TP, FP, FN)

    def Compute_PR_REC_F1_selection_re(self):
        TP = sum([x
                  for doc_name in self.TPs_re
                  for re in self.TPs_re[doc_name]
                  for x in self.TPs_re[doc_name][re]])
        FP = sum([x
                  for doc_name in self.FPs_re
                  for re in self.FPs_re[doc_name]
                  for x in self.FPs_re[doc_name][re]])
        FN = sum([x
                  for doc_name in self.FNs_re
                  for re in self.FNs_re[doc_name]
                  for x in self.FNs_re[doc_name][re]])
        return self.Compute_PR_REC_F1(TP, FP, FN)

    def Compute_PR_REC_F1(self, TP, FP, FN):
        precision = self.CalculatePrecision(TP, FP)
        recall = self.CalculateRecall(TP, FN)
        F1 = self.CalculateF1(precision, recall)
        support = self.CalculateSupport(TP, FN)

        return round(precision, MAX_ROUND), \
               round(recall, MAX_ROUND), \
               round(F1, MAX_ROUND), \
               round(support, MAX_ROUND)

    def Compute_PR_REC_F1_document_pe(self, doc_name):
        TP = sum([x
                  for pe in self.TPs_pe[doc_name]
                  for x in self.TPs_pe[doc_name][pe]])
        FP = sum([x
                  for pe in self.FPs_pe[doc_name]
                  for x in self.FPs_pe[doc_name][pe]])
        FN = sum([x
                  for pe in self.FNs_pe[doc_name]
                  for x in self.FNs_pe[doc_name][pe]])

        return self.Compute_PR_REC_F1(TP, FP, FN)



    def Compute_PR_REC_F1_document_re(self, doc_name):
        TP = sum([x
                  for re in self.TPs_re[doc_name]
                  for x in self.TPs_re[doc_name][re]])
        FP = sum([x
                  for re in self.FPs_re[doc_name]
                  for x in self.FPs_re[doc_name][re]])
        FN = sum([x
                  for re in self.FNs_re[doc_name]
                  for x in self.FNs_re[doc_name][re]])

        return self.Compute_PR_REC_F1(TP, FP, FN)


    def Compute_PR_REC_F1_relation_type(self, rel):
        TP = sum([x
                  for doc_name in self.TPs_re
                  for x in self.TPs_re[doc_name][rel]])
        FP = sum([x
                  for doc_name in self.FPs_re
                  for x in self.FPs_re[doc_name][rel]])
        FN = sum([x
                  for doc_name in self.FNs_re
                  for x in self.FNs_re[doc_name][rel]])

        return self.Compute_PR_REC_F1(TP, FP, FN)


    def Compute_PR_REC_F1_process_element(self, process_element):
        TP = sum([x
                  for doc_name in self.TPs_pe
                  for x in self.TPs_pe[doc_name][process_element]])
        FP = sum([x
                  for doc_name in self.FPs_pe
                  for x in self.FPs_pe[doc_name][process_element]])
        FN = sum([x
                  for doc_name in self.FNs_pe
                  for x in self.FNs_pe[doc_name][process_element]])

        return self.Compute_PR_REC_F1(TP, FP, FN)

    def CalculatePrecision(self, TP, FP):
        try:
            return TP /(TP + FP)
        except ZeroDivisionError:
            return 0

    def CalculateRecall(self, TP, FN):
        try:
            return  TP / (TP + FN)
        except ZeroDivisionError:
            return 0

    def CalculateF1(self, precision, recall):
        try:
            # https://en.wikipedia.org/wiki/F-score
            return 2*(precision*recall) / (precision+recall) # equals to TP / (TP + 1/2*(FP+FN))
        except ZeroDivisionError:
            return  0

    def CalculateSupport(self, TP, FN):
        return TP+FN
