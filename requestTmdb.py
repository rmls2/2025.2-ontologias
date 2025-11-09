import json
import os
import requests
import apiKey


API_KEY = apiKey.KEY
movies_id = []
qtd_filmes = 0

while qtd_filmes <= 2:
    nome_filme = input("Digite o nome do filme!")
    movieByName = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={nome_filme.replace(' ', '-')}')
    dados = movieByName.json()
    try:
        movies_id.append(dados['results'][0]['id'])
    except IndexError:
        print("Nome não encontrado, escolha outro título!")
    finally:
        qtd_filmes+=1
    

for id in movies_id:
    movie = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}').json()
    credits = requests.get(f'https://api.themoviedb.org/3/movie/{id}/credits?api_key={API_KEY}').json()

    diretores = [p['name'] for p in credits['crew'] if p['job'] == 'Director']
    produtores = [p['name'] for p in credits['crew'] if p['job'] == 'Producer']
    roteirista = [p['name'] for p in credits['crew'] if p['job'] == 'Writer']
    atores = [a['name'] for a in credits['cast'][:100]]
    colecao =  movie['belongs_to_collection']['name'] if movie['belongs_to_collection'] else ''   

    movie_dict = {
            "title" : movie['title'],
            "genres": movie['genres'],
            "language": movie['original_language'],
            "country": movie['origin_country'][0] if len(movie['origin_country']) else movie['origin_country'] ,
            'director': diretores[0] if len(diretores) == 1 else diretores,
            'producer': produtores[0] if len(produtores) == 1 else produtores,
            'writer': roteirista[0] if len(roteirista) == 1 else roteirista,
            'actors': atores,
            'colection': colecao


    }
    pasta_destino = 'jsons_movies'
    nome_arquivo = f"{movie_dict['title']}.json"
    caminho_completo = os.path.join(pasta_destino, nome_arquivo)

    os.makedirs(pasta_destino, exist_ok=True)
    print(f"Pasta '{pasta_destino}' verificada/criada.")

    try:
        with open(caminho_completo, 'w', encoding='utf-8') as arquivo_json:
            json.dump(
                movie_dict,
                arquivo_json,
                indent=4,
                sort_keys=False, # Opcional: para ordenar as chaves
                ensure_ascii=False # Importante para caracteres especiais (acentos, etc.)
            )
        print(f"Sucesso! Dados salvos em: {caminho_completo}")

    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")


