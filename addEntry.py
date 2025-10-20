from entityClasses import *
import json
import glob
import re #(provavelmente para achar indivíduos já incluídos)
import os

CONVERT_DICT = {'genres': 'Genero',
                'language': 'Idioma',
                'country': 'Pais',
                'colection': 'Colecao',
                'actors': 'Ator',
                'writer': 'Roteirista',
                'producer': 'Produtor',
                'director': 'Diretor',
                'title': 'Filme',
                #'publisher': 'Distribuidora',
                #'productions': 'Produtora',
                }

JSON_PATHS = glob.glob('jsons_movies/*.json')#['jsons_movies/The Matrix.json']
ONTO_PATH = 'imdb-onto.owl'
ONTO_URL = 'http://www.semanticweb.org/travel-ontology/imdb-ontology'


if(os.path.isfile('base.owl')):
    file = open('base.owl', 'r')
    read_file = file.read()
    file.close()
else:
    read_file = f'''<?xml version="1.0"?>
<rdf:RDF xmlns="{ONTO_URL}"
     xml:base="{ONTO_URL}"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <owl:Ontology rdf:about="{ONTO_URL}"/>

</rdf:RDF>'''

read_file = read_file.split('\n') 
file_tail = read_file.pop()


for json_entry in JSON_PATHS:
    with open(json_entry, 'r') as file:
        new_info = json.load(file)

    for key, value in new_info.items():
        if(isinstance(value, list)):
            for indiv in value:
                if(isinstance(indiv, str)):
                    new_entry = Individual(indiv)
                    new_entry.setClass(CONVERT_DICT[key])
                elif(isinstance(indiv, dict)):
                    name = indiv['name']
                    new_entry = Individual(name)
                    new_entry.setClass(CONVERT_DICT[key])

                read_file.append(str(new_entry))

        elif(isinstance(value, str)):
            new_entry = Individual(value)
            new_entry.setClass(CONVERT_DICT[key])

            if(key=='title'):
                if(isinstance(new_info['genres'], dict)):
                    new_entry.setObjProperty('temGenero', new_info['genres']['name'])
                else:
                    for g in new_info['genres']:
                        new_entry.setObjProperty('temGenero', g['name'])

                for a in new_info['actors']:
                    new_entry.setObjProperty('temAtor', a)

                if(new_info['colection']!=""):
                    new_entry.setObjProperty('pertenceAColecao', new_info['colection'])

                for json_key, obj_prop in zip(['director','producer','writer','country','language'], ['temDiretor','temProdutor','temRoteirista','temPaisDeProducao','temIdiomaOriginal']):
                    if(isinstance(new_info[json_key], str) and len(new_info[json_key])>0):
                        new_entry.setObjProperty(obj_prop, new_info[json_key])
                    elif(isinstance(new_info[json_key], list)):
                        for d in new_info[json_key]:
                            new_entry.setObjProperty(obj_prop, d)

            read_file.append(str(new_entry))

read_file.append(file_tail)
read_file = '\n'.join(read_file)  

with open(ONTO_PATH, 'w') as file:
    file.write(read_file)