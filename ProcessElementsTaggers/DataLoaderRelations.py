import codecs
import sklearn
from nltk import pos_tag
class DataLoader:
    def __init__(self):
        self.training_dataset = None
        self.testing_dataset = None
    
    def LoadDataset(self,
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
        
        print(len(sentences))
        self.data = sentences
        train_perc = .85
        self.training_dataset, self.testing_dataset = sklearn.model_selection.train_test_split(sentences, train_size=train_perc, random_state=13, shuffle=True)
        
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
