class Entity():
    url = 'http://www.semanticweb.org/travel-ontology/imdb-ontology'
    ent_type = None
    def __init__(self, label):
        self.label = label
        self.url_label = self._toURL(label)
        self.relations = {}

    def _toURL(self, in_str:str):
        if(in_str[:7] != 'http://'):
            in_str = ''.join([x.capitalize() for x in in_str.split()])
            return self.url + '#' + in_str
        return in_str

    def __str__(self):
        out_str = f'\t<owl:{self.ent_type} rdf:about="{self.url_label}">'

        for key, value in self.relations.items():
            out_str = out_str + f'\n\t\t<{key} rdf:{value["rdf"]}="{value["item"]}"'
            if(value['rdf'] == 'resource'):
                out_str = out_str + '/>'
            elif(value['rdf'] == 'datatype'):
                out_str = out_str + f'>{value["data_value"]}</{key}>'

        out_str = out_str + f'\n\t\t<rdfs:label xml:lang="pt">{self.label}</rdfs:label>\n\t</owl:{self.ent_type}>\n'

        return out_str

#    <rdf:type rdf:resource="http://www.example.org/travel-ontology#Cidade"/>
#    <localizadaEm rdf:resource="http://www.example.org/travel-ontology#Europa"/>
#    <temAeroporto rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</temAeroporto>
#    <rdfs:label>Lisboa</rdfs:label>
#</owl:NamedIndividual>'''

class Classes(Entity):
    ent_type = 'Class'
    def __init__(self, name):
        super().__init__(name)

    # fazemos alguma coisa mais elaborada para a classe pai?
    # adicionamos uma expressão booleana, por exemplo?
    def setParentClass(self, class_name):
        self.relations['rdfs:subClassOf'] = {'rdf': 'resource',
                                             'item': self._toURL(class_name)}
        
    def setDisjointClass(self, class_name):
        self.relations['owl:disjointWith'] = {'rdf': 'resource',
                                              'item': self._toURL(class_name)}

class ObjectProperty(Entity):
    ent_type = 'ObjectProperty'
    def __init__(self, name):
        super().__init__(name)

    def setCharacteristic(self, chara):
        if(chara not in ['Functional', 'InverseFunctional', 'Transitive', 'Symmetric', 'Asymmetric', 'Reflexive', 'Irreflexive']):
            raise ValueError(f"Characteristic not found: {chara}")
        
        self.relations['rdf:type'] = {'rdf': 'resource',
                                      'item': f"http://www.w3.org/2002/07/owl#{chara}Property"}
    
    def setInverseOf(self, obj_property):
        self.relations['owl:inverseOf'] = {'rdf': 'resource',
                                           'item': obj_property}

    def setDomain(self, ddomain):
        self.relations['rdfs:domain'] = {'rdf': 'resource', 'item': self._toURL(ddomain)}

    def setRange(self, drange):
        self.relations['rdfs:range'] =  {'rdf': 'resource', 'item': f"http://www.w3.org/2001/XMLSchema#{drange}"}

class DataProperty(Entity):
    ent_type = 'DatatypeProperty'
    def __init__(self, label):
        super().__init__(label)

    def setDomain(self, ddomain):
        self.relations['rdfs:domain'] = {'rdf': 'resource', 'item': self._toURL(ddomain)}

    def setRange(self, drange):
        self.relations['rdfs:range'] =  {'rdf': 'resource', 'item': f"http://www.w3.org/2001/XMLSchema#{drange}"}

class Individual(Entity):
    ent_type = 'NamedIndividual'
    def __init__(self, label):
        super().__init__(label)

    def setClass(self, class_name):
        self.relations['rdf:type'] = {'rdf': 'resource', 
                                      'item':self._toURL(class_name)}

    def setObjProperty(self, obj_property, value):
        self.relations[obj_property] = {'rdf': 'resource',
                                        'item': self._toURL(value)}

    def setDataProperty(self, data_property:DataProperty, value):
        self.relations[data_property.label] = {'rdf': 'datatype', 
                                               'item': data_property.relations['rdfs:range']['item'],
                                               'data_value': value}