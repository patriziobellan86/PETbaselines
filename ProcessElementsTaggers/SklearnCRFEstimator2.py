import numpy as np
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer
import pycrfsuite
from itertools import chain
from sklearn.metrics import multilabel_confusion_matrix


class sklearncrfestimator:
    def __init__(self):
        pass

    def word2features(self,
                      sent,
                      i):
        word = sent[i][0]
        postag = sent[i][1]
        features = [
            'bias',
            'word.lower=' + word.lower(),
            'word[-3:]=' + word[-3:],
            'word[-2:]=' + word[-2:],
            'word.isupper=%s' % word.isupper(),
            'word.istitle=%s' % word.istitle(),
            'word.isdigit=%s' % word.isdigit(),
            'postag=' + postag,
            'postag[:2]=' + postag[:2],
        ]
        if i > 0:
            word1 = sent[i - 1][0]
            postag1 = sent[i - 1][1]
            features.extend([
                '-1:word.lower=' + word1.lower(),
                '-1:word.istitle=%s' % word1.istitle(),
                '-1:word.isupper=%s' % word1.isupper(),
                '-1:postag=' + postag1,
                '-1:postag[:2]=' + postag1[:2],
            ])
        else:
            features.append('BOS')

        if i < len(sent) - 1:
            word1 = sent[i + 1][0]
            postag1 = sent[i + 1][1]
            features.extend([
                '+1:word.lower=' + word1.lower(),
                '+1:word.istitle=%s' % word1.istitle(),
                '+1:word.isupper=%s' % word1.isupper(),
                '+1:postag=' + postag1,
                '+1:postag[:2]=' + postag1[:2],
            ])
        else:
            features.append('EOS')

        return features

    def sent2features(self,
                      sent):
        return [self.word2features(sent, i) for i in range(len(sent))]

    def sent2labels(self,
                    sent):
        return [label for token, postag, label in sent]

    def sent2tokens(self,
                    sent):
        return [token for token, postag, label in sent]

    # def bio_classification_report(self,
    #                               y_true,
    #                               y_pred):
    #     """
    #     Classification report for a list of BIO-encoded sequences.
    #     It computes token-level metrics and discards "O" labels.
    #
    #     Note that it requires scikit-learn 0.15+ (or a version from github master)
    #     to calculate averages properly!
    #     """
    #     lb = LabelBinarizer()
    #     y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
    #     y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))
    #
    #     tagset = set(lb.classes_) - {'O'}
    #     tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    #     class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}
    #
    #     return classification_report(
    #         y_true_combined,
    #         y_pred_combined,
    #         labels=[class_indices[cls] for cls in tagset],
    #         target_names=tagset,
    #         # MY ADD
    #         digits=3,
    #         output_dict=False,
    #     )
    #
    # def print_transitions(self,
    #                       trans_features):
    #     for (label_from, label_to), weight in trans_features:
    #         print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))
    #
    # def print_state_features(self,
    #                          state_features):
    #     for (attr, label), weight in state_features:
    #         print("%0.6f %-6s %s" % (weight, label, attr))

    def CrossValidation(self,
                        train_folds,
                        test_folds,
                        save_model_path):
        # scores = list()
        training_predictions = list()
        testing_predictions = list()

        for n_fold, item in enumerate(zip(train_folds, test_folds)):
            train_fold, test_fold = item

            model_filename = save_model_path.joinpath('k_{}_pysuitecrfmodel.model'.format(n_fold))

            self.Train(str(model_filename),
                       train_fold)
            training_prediction = self.TestModel(str(model_filename),
                                                 train_fold)

            training_prediction = self._convert_predictions_into_entities(training_prediction)
            training_predictions.append(training_prediction)
            testing_prediction = self.TestModel(str(model_filename),
                                   test_fold)
            testing_prediction = self._convert_predictions_into_entities(testing_prediction)
            testing_predictions.append(testing_prediction)
        return {'training-predictions': training_predictions,
                'testing-predictions': testing_predictions}

    def _convert_predictions_into_entities(self,
                                           predictions):

        entities_in_sentences = list()
        for sentence in predictions:
            entities_in_sentence = list()
            pe_type = ''
            entity_range = list()
            print(sentence)
            for n_w, word in enumerate(sentence):
                if word == 'O':
                    if entity_range:
                        # record previous entity
                        entities_in_sentence.append([pe_type, entity_range])
                        entity_range = list()

                elif word.startswith('B-'):
                    if entity_range:
                        # record previous entity
                        entities_in_sentence.append([pe_type, entity_range])
                        entity_range = list()
                    pe_type = word[2:]
                    entity_range.append(n_w)

                elif word.startswith('I-'):
                    entity_range.append(n_w)

                elif word.startswith('S-'):
                    if entity_range:
                        # record previous entity
                        entities_in_sentence.append([pe_type, entity_range])
                        entity_range = list()

                    pe_type = word[2:]
                    entity_range.append(n_w)
                    entities_in_sentence.append([pe_type, entity_range])

                    entity_range = list()

                elif word.startswith('E-'):
                    entity_range.append(n_w)
                    entities_in_sentence.append([pe_type, entity_range])

                    entity_range = list()

            entities_in_sentences.append(entities_in_sentence)
        return entities_in_sentences


    def Train(self,
              model_filename,
              train_sents):

        msg = ''

        X_train = [self.sent2features(s) for s in train_sents]
        y_train = [self.sent2labels(s) for s in train_sents]

        # https: // python - crfsuite.readthedocs.io / en / latest / pycrfsuite.html
        trainer = pycrfsuite.Trainer(verbose=False)

        for xseq, yseq in zip(X_train, y_train):
            trainer.append(xseq, yseq)
        trainer.set_params({
            'c1': 1.0,   # coefficient for L1 penalty
            'c2': 1e-3,  # coefficient for L2 penalty
            'max_iterations': 50,  # stop earlier

            # include transitions that are possible, but not observed
            'feature.possible_transitions': True
        })
        # print('trainer.params()', trainer.params())
        msg_ = 'trainer.params()'+' '.join(trainer.params())+'\n'
        msg = msg+msg_
        # self.ent_log_text.insert('end', msg)
        trainer.train(model_filename)
        # print('trainer.logparser.last_iteration', trainer.logparser.last_iteration)
        msg = msg +'trainer.logparser.last_iteration'+str(trainer.logparser.last_iteration)

        # print(len(trainer.logparser.iterations), trainer.logparser.iterations[-1])
        msg = msg+str(len(trainer.logparser.iterations))+str(trainer.logparser.iterations[-1])

        return msg

    def LoadModel(self,
                  model_filename):
        tagger = pycrfsuite.Tagger()
        tagger.open(model_filename)
        return tagger

    #
    # def Test(self,
    #         model_filename,
    #         test_sents):
    #
    #     #  load tagger model
    #     tagger = self.LoadModel(model_filename)
    #
    #     #  Load X, Y test set
    #     X_test = [self.sent2features(s) for s in test_sents]
    #     y_test = [self.sent2labels(s) for s in test_sents]
    #
    #     example_sent = test_sents[0]
    #     print(' '.join(self.sent2tokens(example_sent)), end='\n\n')
    #
    #     print("Predicted:", ' '.join(tagger.tag(self.sent2features(example_sent))))
    #     print("Correct:  ", ' '.join(self.sent2labels(example_sent)))
    #
    #     y_pred = [tagger.tag(xseq) for xseq in X_test]
    #     print(self.bio_classification_report(y_test, y_pred))
    #     report = self.bio_classification_report(y_test, y_pred)
    #
    #     msg = self.bio_classification_report(y_test, y_pred)+'\n'
    #     # self.ent_log_text.insert('end', msg)
    #
    #     info = tagger.info()
    #     print(info)
    #
    #     print("Top likely transitions:")
    #     self.print_transitions(Counter(info.transitions).most_common(15))
    #
    #     print("\nTop unlikely transitions:")
    #     self.print_transitions(Counter(info.transitions).most_common()[-15:])
    #
    #     print("Top positive:")
    #     self.print_state_features(Counter(info.state_features).most_common(20))
    #
    #     print("\nTop negative:")
    #     self.print_state_features(Counter(info.state_features).most_common()[-20:])
    #
    #     return msg


    def TestModel(self,
                  model_filename,
                  test_sents):

        #  load tagger model
        tagger = self.LoadModel(model_filename)

        #  Load X, Y test set
        X_test = [self.sent2features(s) for s in test_sents]
        y_test = [self.sent2labels(s) for s in test_sents]

        y_pred = [tagger.tag(xseq) for xseq in X_test]
        return y_pred
        #
        # lb = LabelBinarizer()
        # y_true_combined = lb.fit_transform(list(chain.from_iterable(y_test)))
        # y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))
        #
        # tagset = set(lb.classes_) # - {'O'}
        # tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
        # class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}
        # mcm = multilabel_confusion_matrix(y_true_combined, y_pred_combined)
        # # print(len(tagset), len(mcm))
        # results = dict()
        # for i in enumerate(tagset):
        #     tag = i[1]
        #     ind = i[0]
        #     # print(tag)
        #     # print(mcm[ind])
        #     # true negatives 0, 0}
        #     # false negatives 1, 0}`,
        #     # true positives 1, 1}
        #     # false positives 0, 1}`.
        #     results[tag] = {'TP': mcm[ind][1][1],
        #                     'TN': mcm[ind][0][0],
        #                     'FP': mcm[ind][0][1],
        #                     'FN': mcm[ind][1][0],}
        # return results



    def TestScores_OLD(self,
            model_filename,
            test_sents):

        #  load tagger model
        tagger = self.LoadModel(model_filename)

        #  Load X, Y test set
        X_test = [self.sent2features(s) for s in test_sents]
        y_test = [self.sent2labels(s) for s in test_sents]

        y_pred = [tagger.tag(xseq) for xseq in X_test]

        lb = LabelBinarizer()
        y_true_combined = lb.fit_transform(list(chain.from_iterable(y_test)))
        y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))

        tagset = set(lb.classes_) # - {'O'}
        tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
        class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}
        mcm = multilabel_confusion_matrix(y_true_combined, y_pred_combined)
        # print(len(tagset), len(mcm))
        results = dict()
        for i in enumerate(tagset):
            tag = i[1]
            ind = i[0]
            # print(tag)
            # print(mcm[ind])
            # true negatives 0, 0}
            # false negatives 1, 0}`,
            # true positives 1, 1}
            # false positives 0, 1}`.
            results[tag] = {'TP': mcm[ind][1][1],
                            'TN': mcm[ind][0][0],
                            'FP': mcm[ind][0][1],
                            'FN': mcm[ind][1][0],}
        return results