from collections import defaultdict
from copy import deepcopy

class Linker:
    def __init__(self):
        self.__init_variables__()

    def __init_variables__(self):
        self.linkers = list()

    def Parse(self, document_elements):
        elements = self._transform_elements_in_list(document_elements)
        relations = list()
        for linker in self.linkers:
            relations = linker.Parse(elements, relations)

        # relations = list(set(relations))  #  avoid duplicates
        document_relations = self._transform_relations_in_document_relations(relations)

        return document_relations

    def AddLinker(self, linker):
        self.linkers.append(linker)

    def GetLinker(self):
        return self.linkers

    def _transform_elements_in_list(self,
                                    elements):
        #['Activity']
        # [[[5], [12]], [[4]], [[5], [14]], [[8]], [[4]], [[14]], [[14], [18], [25]]]

        # return: list of elements [n_sent, element_type, span]
        elements_list = list()

        for ele_type in elements:
            for n_sent in range(len(elements[ele_type])):
                for ele_range in elements[ele_type][n_sent]:
                    elements_list.append([n_sent, ele_type, ele_range])
        return elements_list

    def _transform_relations_in_document_relations(self,
                                                   relations):
        document_relations = defaultdict(list)
        for relation in relations:
            source, rel_type, target = relation

            source_n_sent = 'n_sent_{}'.format(source[0])
            source_range = ' '.join([str(n) for n in source[2]]).strip()
            source_str = '{} {}'.format(source_n_sent,
                                        source_range)

            target_n_sent = 'n_sent_{}'.format(target[0])
            target_range = ' '.join([str(n) for n in target[2]]).strip()
            target_str = '{} {}'.format(target_n_sent,
                                        target_range)

            document_relations[source_str].append([rel_type, target_str])
        return document_relations


############## LINKER ################
class LinkerBaseClass:
    #  ELEMENTS
    XOR_GATEWAY = 'XOR Gateway'
    AND_GATEWAY = 'AND Gateway'
    ACTIVITY = 'Activity'
    CONDITION_SPECIFICATION = 'Condition Specification'

    FURTHER_SPECIFICATION = 'Further Specification'
    ACTIVITY_DATA = 'Activity Data'
    ACTOR = 'Actor'

    BEHAVIORAL_ELEMENTS = [XOR_GATEWAY,
                           AND_GATEWAY,
                           ACTIVITY,
                           CONDITION_SPECIFICATION]
    GATEWAYS_ELEMENTS = [XOR_GATEWAY,
                         AND_GATEWAY]
    #  RELATIONS
    SEQUENCE_FLOW_RELATION = 'a4Flows'
    SAME_GATEWAY_RELATION  = 'a6SameGateway'
    BEHAVIORAL_RELATIONS = [SEQUENCE_FLOW_RELATION,
                            SAME_GATEWAY_RELATION]

    ACTOR_RECIPIENT_RELATION = 'Actor Recipient'
    ACTOR_PERFORMER_RELATION = 'Actor Performer'

    USES_RELATION = 'a2Uses'
    FURTHER_SPECIFICATION_RELATION = 'a5FurtherSpecification'

    def __init__(self):
        pass

    def Parse(self,
              elements,
              relations):
        """

        :param relations: is a list of relations [source, rel type, target]
        :param elements: is a list of elements [n_sent, element_type, span]
        :return:
            a new list of relations
        """
        new_relations = list()
        raise NotImplementedError('You must implement this method')

    def sort_elements(self,
                     elements):
        return deepcopy(sorted(elements, key=lambda x: (x[0], x[2][0])))

    def filter_elements(self,
                        elements,
                        filter):
        # filter is a list of element types to keep
        return deepcopy([ele for ele in elements
                             if ele[1] in filter])

    def filter_relations(self,
                         relations,
                         filter):
        # filter is a list of element types to keep
        return deepcopy([rel for rel in relations
                              if rel[1] in filter])

    def _convert_element_into_tuple(self,
                                    element):
        return tuple([element[0], element[1], tuple(element[2])])

    def _convert_element_into_list(self,
                                   element):
        return [element[0], element[1], list(element[2])]

    def _calculate_elements_distance_same_sentence(self,
                                                   element_1,
                                                   element_2):
        elements_sorted = sorted([element_1, element_2], key=lambda x: x[2][0])
        distance = elements_sorted[-1][2][0] - elements_sorted[0][2][-1] # begin of the right most ele - end of the left most ele

        return distance

    def _get_sentences_len(self,
                           elements):
        #  sentence len is equal to the last tagged element
        sentences_lens = {ele[0]: 0 for ele in elements}
        elements = self.sort_elements(elements)
        for element in elements:
            element_end = element[2][-1]
            element_n_sent = element[0]
            if element_end > sentences_lens[element_n_sent]:
                sentences_lens[element_n_sent] = element_end
        return sentences_lens

    def _calculate_elements_distance_in_sentences(self,
                                                   element_1,
                                                   element_2,
                                                  sentences_len):

        elements_sorted = sorted([element_1, element_2], key=lambda x: x[0]) # sort on n_sent
        # distance is from the end of the first element to the end of its sentence
        dist = sentences_len[elements_sorted[0][0]] - elements_sorted[0][2][-1]
        # plus each sentences len between the first element and the second
        for n_sent in range(elements_sorted[0][0]+1, elements_sorted[1][0]):  # +1 because the first sentece is considerd above
            if n_sent not in sentences_len:
                # in the case sentece was not annotated
                # no penality
                continue
            dist = dist + sentences_len[n_sent]
        # plus the begin of the second element
        dist = dist + elements_sorted[1][2][0]

        return dist

    def _get_closest_element(self,
                             source,
                             elements,
                             sentences_len):
        distances = list()
        for n_element, element in enumerate(elements):
            distance = self._calculate_elements_distance_in_sentences(source,
                                                           element,
                                                           sentences_len)
            distances.append([n_element, distance])
        distance = sorted(distances, key=lambda x: x[1])[0] # [n_item, distance]

        closest_element = elements[distance[0]]

        return closest_element


    def _get_closest_element_same_sentence(self,
                             source,
                             elements):
        distances = list()
        for n_element, element in enumerate(elements):
            distance = self._calculate_elements_distance_same_sentence(source,
                                                                       element)
            distances.append([n_element, distance])
        distance = sorted(distances, key=lambda x: x[1])[0] # [n_item, distance]

        closest_element = elements[distance[0]]

        return closest_element

    def _calculate_elements_distance_same_sentence(self,
                                                   element_1,
                                                   element_2):
        elements_sorted = sorted([element_1, element_2], key=lambda x: x[2][0])
        distance = elements_sorted[-1][2][0] - elements_sorted[0][2][-1] # begin of the right most ele - end of the left most ele

        return distance



###### LINKERS  ###############
class SimplerSequenceFlowLinker(LinkerBaseClass):
    def Parse(self,
              elements,
              relations):
        new_relations = list()

        # sort the element
        elements_sorted = self.sort_elements(elements)
        # filter out not behavioral elements
        elements_filtered = self.filter_elements(elements_sorted, self.BEHAVIORAL_ELEMENTS)

        # makes a connection between each element
        for n_ele in range(len(elements_filtered)-1):
            relation = [elements_filtered[n_ele], self.SEQUENCE_FLOW_RELATION, elements_filtered[n_ele+1]]
            new_relations.append(relation)
        return new_relations

class SimplerSameGatewayLinker(LinkerBaseClass):
    def Parse(self,
              elements,
              relations):
        new_relations = list()
        new_relations = deepcopy(relations)
        elements_sorted = self.sort_elements(elements)
        # filter out not behavioral elements
        elements_filtered = self.filter_elements(elements_sorted, self.BEHAVIORAL_ELEMENTS)
        xors = self.filter_elements(elements_filtered, [self.XOR_GATEWAY])
        ands = self.filter_elements(elements_sorted, [self.AND_GATEWAY])

        # makes a connection between each gateway of the same type that is in the same sentence or in the next onr
        new_relations.extend(self._strategy(xors))
        new_relations.extend(self._strategy(ands))

        return new_relations

    def _strategy(self, gate_list):
        new_relations = list()
        for n_gate in range(len(gate_list) - 1):
            n_sent, _, gate_range = gate_list[n_gate]
            n_sent_next, _, gate_range_next = gate_list[n_gate+1]
            if n_sent == n_sent_next or n_sent == n_sent_next - 1:
                relation = [gate_list[n_gate], self.SAME_GATEWAY_RELATION, gate_list[n_gate + 1]]
                new_relations.append(relation)
        return new_relations

##### Clean SameGate Flow Relations ######
####  considering the branches      ######

class GatewaysBranchOpener(LinkerBaseClass):
    """
        #  RULE:
        #  IF A GATEWAY IS A TARGET OF A SAME GATEWAY RELATION
        #  REMOVE THE CONNECTION BETWEEN THE PREVIOUS BEHAVIORAL ELEMENT

    """
    def Parse(self,
              elements,
              relations):
        new_relations = list()
        new_relations = deepcopy(relations)
        # sort the element
        elements_sorted = self.sort_elements(elements)

        # filter out not behavioral elements
        elements_filtered = self.filter_elements(elements_sorted, self.BEHAVIORAL_ELEMENTS)

        tot_n_sents = elements_filtered[-1][0]

        # filer out not behavioral relations
        relations_filtered = self.filter_relations(relations, self.BEHAVIORAL_RELATIONS)

        target_of_flows_to_remove = list()  # list of sequence flow to remove
        for rel in relations_filtered:
            source, rel_type, target = rel
            if rel_type == self.SAME_GATEWAY_RELATION:
                target_of_flows_to_remove.append(target)

        new_relations = [rel for rel in new_relations
        if not (rel[2] in target_of_flows_to_remove and rel[1] == self.SEQUENCE_FLOW_RELATION)]

        return new_relations


class GatewaysDefaultBranchAdder(LinkerBaseClass):
    """
        #  RULE:
        #  IF THERE IS A GATEWAY WITHOUT A SAME GATEWAY RELATION
        #  ADD A DEFAULT BRANCH LINK (SEQUENCE FLOW) BETWEEN THE GATEWAY AND THE SECOND NEXT Activity
        #  ex. sent = [act1, gate1, act2, act3] it adds a flow (gate1,act3)
        #  if not possible, do not add anything
    """

    def Parse(self,
              elements,
              relations):
        new_relations = list()
        new_relations = deepcopy(relations)
        # sort the element
        elements_sorted = self.sort_elements(elements)
        # filter out not behavioral elements
        elements_filtered = self.filter_elements(elements_sorted, self.BEHAVIORAL_ELEMENTS)

        tot_n_sents = elements_filtered[-1][0]
        # filer out not behavioral relations
        relations_filtered = self.filter_relations(relations, [self.SAME_GATEWAY_RELATION])

        #  detect gateways w/o a same gateway relation
        all_gateways = self.filter_elements(elements, self.GATEWAYS_ELEMENTS)
        all_gateways = set([
                            self._convert_element_into_tuple(item) #tuple([item[0], item[1], tuple(item[2])])
                                for item in all_gateways])
        gateways_same = set()
        for rel in relations_filtered:
            source, _, target = rel
            gateways_same.add(self._convert_element_into_tuple(source)) #tuple([source[0], source[1], tuple(source[2])]))
            gateways_same.add(self._convert_element_into_tuple(target)) #tuple([target[0], target[1], tuple(target[2])]))
        gateways_alone = list(set(all_gateways).difference(gateways_same))

        #  for each gateway alone, retrieve the second next process element
        for alone in gateways_alone:
            second_next_process_element = self._get_second_next_process_element(elements_filtered,
                                                                                self._convert_element_into_list(alone))
            if second_next_process_element:
                #  add relation
                relation = [alone,
                            self.SEQUENCE_FLOW_RELATION,
                            second_next_process_element]
                new_relations.append(relation)

        return new_relations

    def _get_second_next_process_element(self,
                                         elements,
                                         source_element):
        second = None
        elements = deepcopy(self.sort_elements(elements))
        index_source = elements.index(source_element)
        is_first_next_activity = False
        for possible_index in range(index_source+1, len(elements)):
            _, ele_type, _ = elements[possible_index]
            if is_first_next_activity and ele_type == self.ACTIVITY:
                return elements[possible_index]

            if ele_type == self.ACTIVITY:
                is_first_next_activity = True

        return False


#
# class GatewaysBranchCloser(LinkerBaseClass):
#     """
#         #  RULE:
#         #  IF THERE IS A BRANCH OPEN, CLOSE IT TO THE NEXT COMMON ACTIVITY
#         #  EX. [act1, g1, act2, g2, act3, act4]
#         #  g1 same gate g2
#         #  connect act2 and act3 to act4
#
#         #  if not possible, do not add anything
#     """
#
#     def Parse(self,
#               elements,
#               relations):
#         new_relations = list()
#         new_relations = deepcopy(relations)
#         # sort the element
#         elements_sorted = self.sort_elements(elements)
#         # filter out not behavioral elements
#         elements_filtered = self.filter_elements(elements_sorted, self.BEHAVIORAL_ELEMENTS)
#
#         tot_n_sents = elements_filtered[-1][0]
#         # filer out not behavioral relations
#         relations_filtered = self.filter_relations(relations, [self.SAME_GATEWAY_RELATION])
#
#         #  detect gateways w/o a same gateway relation
#         all_gateways = self.filter_elements(elements, self.GATEWAYS_ELEMENTS)
#         all_gateways = set([
#                             self._convert_element_into_tuple(item) #tuple([item[0], item[1], tuple(item[2])])
#                                 for item in all_gateways])
#         gateways_same = set()
#         for rel in relations_filtered:
#             source, _, target = rel
#             gateways_same.add(self._convert_element_into_tuple(source)) #tuple([source[0], source[1], tuple(source[2])]))
#             gateways_same.add(self._convert_element_into_tuple(target)) #tuple([target[0], target[1], tuple(target[2])]))
#         gateways_alone = list(set(all_gateways).difference(gateways_same))
#
#         #  for each gateway alone, retrieve the second next process element
#         for alone in gateways_alone:
#             second_next_process_element = self._get_second_next_process_element(elements_filtered,
#                                                                                 self._convert_element_into_list(alone))
#             if second_next_process_element:
#                 #  add relation
#                 relation = [alone,
#                             self.SEQUENCE_FLOW_RELATION,
#                             second_next_process_element]
#                 new_relations.append(relation)
#
#         return new_relations
#
#     def _get_next_common_element(self,
#                                          elements,
#                                          source_element):
#         #  a common element can be an activity or another gateway
#
#         second = None
#         elements = deepcopy(self.sort_elements(elements))
#         index_source = elements.index(source_element)
#         is_first_next_activity = False
#         for possible_index in range(index_source+1, len(elements)):
#             _, ele_type, _ = elements[possible_index]
#             if is_first_next_activity and ele_type == self.ACTIVITY:
#                 return elements[possible_index]
#
#             if ele_type == self.ACTIVITY:
#                 is_first_next_activity = True
#
#         return False
####### FURTHER SPECIFICATION LINKER

class FurtherSpecificationLinker(LinkerBaseClass):
    """
        #  RULE:
        #  LINK A FURTHER SPECIFICATION TO THE PREVIOUS ACTIVITY
        #  if not possible, adds it to the closest one
    """

    def Parse(self,
              elements,
              relations):
        new_relations = list()
        new_relations = deepcopy(relations)
        # sort the element
        elements_sorted = self.sort_elements(elements)
        # filter out not behavioral elements
        further_specs = self.filter_elements(elements_sorted, [self.FURTHER_SPECIFICATION])
        further_specs = self.sort_elements(further_specs)
        activities = self.filter_elements(elements_sorted, [self.ACTIVITY])
        activities = self.sort_elements(activities)
        tot_n_sents = activities[-1][0]

        for further_spec in further_specs:
            fs_n_sent, _, fs_range = further_spec
            fs_begin = fs_range[0]
            fs_end = fs_range[-1]

            activities_in_sentence = [act for act in activities if act[0]==fs_n_sent]
# # DEV ############################
#             activities_in_sentence = []
            if len(activities_in_sentence) == 1:
                relation = [activities_in_sentence[0], self.FURTHER_SPECIFICATION_RELATION, further_spec]
                new_relations.append(relation)
            elif len(activities_in_sentence) == 0:
                sentences_len = self._get_sentences_len(elements)

                # assign it to the most close activity in the text.
                closest_acitivity = self._get_closest_element(further_spec,
                                                              activities,
                                                              sentences_len)
                relation = [closest_acitivity, self.FURTHER_SPECIFICATION_RELATION, further_spec]
                new_relations.append(relation)

            elif len(activities_in_sentence) > 1:
                distances = list()
                for n_act, act in enumerate(activities_in_sentence):
                    #  compute distance between
                    distance = self._calculate_elements_distance_same_sentence(further_spec, act)
                    distances.append([n_act, distance])
                distance = sorted(distances, key= lambda x:x[1])[0]
                relation = [activities_in_sentence[n_act], self.FURTHER_SPECIFICATION_RELATION, further_spec]
                new_relations.append(relation)
        return new_relations

####  ACTIVITY DATA ######

class ActivityDataLinker(LinkerBaseClass):
    """
        #  RULE:
        #  LINK AN Activity Data TO THE PREVIOUS ACTIVITY
        #  if not possible, adds it to the closest one
    """

    def Parse(self,
              elements,
              relations):
        new_relations = list()
        new_relations = deepcopy(relations)
        # sort the element
        elements_sorted = self.sort_elements(elements)
        # filter out not behavioral elements
        actdata = self.filter_elements(elements_sorted, [self.ACTIVITY_DATA])
        actdata = self.sort_elements(actdata)
        activities = self.filter_elements(elements_sorted, [self.ACTIVITY])
        activities = self.sort_elements(activities)

        for ad in actdata:
            ad_n_sent, _, ad_range = ad
            ad_begin = ad_range[0]
            ad_end = ad_range[-1]
            activities_in_sentence = [act for act in activities if act[0]==ad_n_sent]
# # DEV ############################
#             activities_in_sentence = []
            if len(activities_in_sentence) == 1:
                relation = [activities_in_sentence[0], self.USES_RELATION, ad]
                new_relations.append(relation)

            elif len(activities_in_sentence) == 0:
                sentences_len = self._get_sentences_len(elements)
                #  exclude activities follows the activtiy data
                activities_prev = list(filter(lambda x: x[0] < ad_n_sent, activities))
                #  resolve rare but possible situations
                if len(activities_prev) == 0:
                    activities_prev = activities
                # assign it to the most close activity in the text.
                closest_acitivity = self._get_closest_element(ad,
                                                              activities_prev,
                                                              sentences_len)
                relation = [closest_acitivity, self.USES_RELATION, ad]
                new_relations.append(relation)

            elif len(activities_in_sentence) > 1:
                #  privilegia le activity on the left, if possible. otherwise, use the right closest one

                # try on the left
                left_activities = list(filter(lambda x: (x[2][0] < ad_begin), activities_in_sentence))
                if len(left_activities):
                    closest_acitivity = self._get_closest_element_same_sentence(ad, left_activities)
                else:
                    #  get the closest on the right
                    closest_acitivity = self._get_closest_element_same_sentence(ad, activities_in_sentence)
                relation = [closest_acitivity, self.USES_RELATION, ad]
                new_relations.append(relation)
        return new_relations


####  ACTOR ######

class ActorLinker(LinkerBaseClass):
    """
        #  RULE:
        #  LINK AN ActorTO its closest ACTIVITY
        # if actor is on the right -> actor recipient
        # if actor is on the left -> actor performer

        #  if not possible, adds it to the closest one
    """

    def Parse(self,
              elements,
              relations):
        new_relations = list()
        new_relations = deepcopy(relations)
        # sort the element
        elements_sorted = self.sort_elements(elements)
        # filter out not behavioral elements
        actors = self.filter_elements(elements_sorted, [self.ACTOR])
        actors = self.sort_elements(actors)
        activities = self.filter_elements(elements_sorted, [self.ACTIVITY])
        activities = self.sort_elements(activities)

        for actor in actors:
            actor_n_sent, _, actor_range = actor
            actor_begin = actor_range[0]
            actor_end = actor_range[-1]
            activities_in_sentence = [act for act in activities
                                        if act[0] == actor_n_sent]

#             activities_in_sentence = []
            if len(activities_in_sentence) == 1:
                rel_type = self._get_actor_relation_type(actor,
                                                         activities_in_sentence[0])
                relation = self.create_relation(activities_in_sentence[0], rel_type, actor)

            elif len(activities_in_sentence) == 0:
                sentences_len = self._get_sentences_len(elements)
                closest_acitivity = self._get_closest_element(actor,
                                                              activities,
                                                              sentences_len)
                # since they are not in the same sentence, i compare sentence number
                if closest_acitivity[0] > actor[0]:
                    relation = self.create_relation(closest_acitivity, self.ACTOR_PERFORMER_RELATION, actor)
                else:
                    relation = self.create_relation(closest_acitivity, self.ACTOR_PERFORMER_RELATION, actor)

            elif len(activities_in_sentence) > 1:
                # link the actor to the closest activity
                closest_acitivity = self._get_closest_element_same_sentence(actor, activities_in_sentence)
                left_activities = list(filter(lambda x: (x[2][0] < actor_begin), activities_in_sentence))
                if closest_acitivity in left_activities:
                    relation = self.create_relation(closest_acitivity, self.ACTOR_RECIPIENT_RELATION, actor)
                else:
                    relation = self.create_relation(closest_acitivity, self.ACTOR_PERFORMER_RELATION, actor)

            new_relations.append(relation)

        return new_relations

    def _get_actor_relation_type(self,
                                 actor,
                                 activity):
        sorted_items = sorted([actor, activity], key=lambda x: x[2][0])
        if sorted_items[0][1] == self.ACTIVITY:
            # if actor is on the right -> actor recipient
            # if actor is on the left -> actor performer
            return self.ACTOR_RECIPIENT_RELATION
        else:
            return self.ACTOR_PERFORMER_RELATION

    def create_relation(self,
                        item1,
                        relation_type,
                        item2):
        if relation_type not in self.BEHAVIORAL_RELATIONS:
            if item1[1] == self.ACTIVITY:
                source = item1
                target = item2
            else:
                source = item2
                target = item1
        else:
            # do no check
            source = item1
            target = item2

        relation = [source, relation_type, target]

        return relation



if __name__ == '__main__':
    from annotationdataset import AnnotationDataset
    from pprint import pprint

    dataset_filename = '/Users/patrizio/Documents/PhD/AnnotationVisualizer/DEVELOPMENT/datasets/LREC_PARSING_ALL.sopap_dataset'
    dataset_to_annotate_filename = '/Users/patrizio/Documents/PhD/AnnotationVisualizer/DEVELOPMENT/datasets/LREC_predicted.sopap_dataset'
    # dataset_filename = dataset_to_annotate_filename

    dataset = AnnotationDataset()
    dataset.LoadDataset(filename=dataset_filename)

    # TEST DEV
    linker = Linker()
    # linker.AddLinker(FurtherSpecificationLinker())
    # linker.AddLinker(ActivityDataLinker())
    linker.AddLinker(ActorLinker())
    for doc_name in dataset.GetGoldStandardDocuments():
        print(doc_name)
        elements = dataset.GetGoldStandardEntities(doc_name)
        relations = linker.Parse(elements)
        dataset.AddPredictedRelationsAnnotation(doc_name,
                                                'Actor_linker',
                                                relations)
        print('relations', len(relations))

