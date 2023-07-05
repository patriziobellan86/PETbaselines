import codecs
import sklearn
from nltk import pos_tag
from glob import glob

class DataLoader:
    def __init__(self,
                 folder):
        self.training_dataset = list()
        self.testing_dataset = list()

        self.LoadData(folder)

    def convert_predictions_into_doc_predictions(self,
                                                 predictions):

        #  load data
        training_folds = list()
        testing_folds = list()

        for n_fold, training_doc in enumerate(sorted(self.experiment_folder.glob('*train-doc-name.*'))):
            training_docs = dict()
            n_sent = 0

            with codecs.open(training_doc, 'r', 'utf-8') as fin:
                for line in fin.readlines():
                    line = line.split('\t')
                    doc_name, n_sent_doc = line
                    n_sent_doc = int(n_sent_doc)
                    doc_sentences = predictions['training-predictions'][n_fold][n_sent: n_sent + n_sent_doc]
                    doc_sentences = self._convert_sentences_into_doc_entities(doc_sentences)
                    training_docs[doc_name] = doc_sentences
                    n_sent = n_sent + n_sent_doc
            training_folds.append(training_docs)

        for n_fold, testing_doc in enumerate(sorted(self.experiment_folder.glob('*test-doc-name.*'))):
            testing_docs = dict()
            n_sent = 0

            with codecs.open(testing_doc, 'r', 'utf-8') as fin:
                for line in fin.readlines():
                    line = line.split('\t')
                    doc_name, n_sent_doc = line
                    n_sent_doc = int(n_sent_doc)
                    doc_sentences = predictions['testing-predictions'][n_fold][n_sent: n_sent + n_sent_doc]
                    doc_sentences = self._convert_sentences_into_doc_entities(doc_sentences)
                    testing_docs[doc_name] = doc_sentences
                    n_sent = n_sent + n_sent_doc
            testing_folds.append(testing_docs)

        return training_folds, testing_folds

    def _convert_sentences_into_doc_entities(self,
                                             sentences):
        n_sents = len(sentences)
        doc_entities = {label: [[] for _ in range(n_sents)]
                            for label in ['Activity',
                                          'Activity Data',
                                          'Actor',
                                          'Condition Specification',
                                          'Further Specification',
                                          'XOR Gateway',
                                          'AND Gateway']}
        for n_sent, sentence in enumerate(sentences):
            for pe_type, pe_range in sentence:
                if pe_type == '':
                    # skip errors
                    continue
                doc_entities[pe_type][n_sent].append(pe_range)

        return doc_entities

    def _load_a_file(self,
                     filename):
        sentences = list()
        sentence = list()
        data = codecs.open(filename, 'r', 'utf-8').readlines()
        for line in data:
            if len(line.strip()) == 0:
                sentence = self._add_postags(sentence)
                sentences.append(sentence)
                sentence = list()
            else:
                sentence.append([x.strip() for x in line.split('\t')])
        return sentences

    def LoadData(self,
                folder):
        self.experiment_folder = folder
        for training_file in sorted(folder.glob('*train.*')):
            data = self._load_a_file(training_file)
            self.training_dataset.append(data)
        for test_file in sorted(folder.glob('*test.*')):
            data = self._load_a_file(test_file)
            self.testing_dataset.append(data)

    def _add_postags(self,
                     sentence):
        pos_tagged = list()
        postag_list = pos_tag(self.GetSentenceWords(sentence))

        for n_word, line in enumerate(sentence):
            pos_tagged.append([*postag_list[n_word], line[1]])
        return pos_tagged

    def GetSentenceWords(self,
                 sentence):
        words = list()
        for w in sentence:
            words.append(w[0])
        return words

    def GetSentenceTags(self,
                        sentence,
                        ):
        tags = list()
        for w in sentence:
            tags.append(w[1])
        return tags
