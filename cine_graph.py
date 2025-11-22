import streamlit as st
import requests
import json
import os
import apiKey
import glob
from addEntry import OWLFile

API_KEY = apiKey.KEY
BASE_FILE = 'base.owl'
OUTPUT_FILE = 'cinegraph_att.owl'

st.set_page_config(page_title="Cine Graph", page_icon="🎬", layout="centered")

# Título central
st.markdown("<h1 style='text-align: center;'>🎬 Cine Graph</h1>", unsafe_allow_html=True)
st.markdown("---")

# Inicializa a lista de inputs na sessão
if "num_campos" not in st.session_state:
    st.session_state.num_campos = 1
if "nomes_filmes" not in st.session_state:
    st.session_state.nomes_filmes = [""]

# Funções para adicionar e remover campos
def add_input():
    st.session_state.num_campos += 1
    st.session_state.nomes_filmes.append("")

def remove_input():
    if st.session_state.num_campos > 1:
        st.session_state.num_campos -= 1
        st.session_state.nomes_filmes.pop()

# Botões de controle
col1, col2, col3 = st.columns(3)
with col1:
    st.button("➕ Adicionar campo", on_click=add_input)
with col2:
    st.button("➖ Remover campo", on_click=remove_input)
with col3:
    pesquisar = st.button("🔍 Pesquisar")

# Campos de input dinâmicos
for i in range(st.session_state.num_campos):
    st.session_state.nomes_filmes[i] = st.text_input(f"Filme {i+1}", value=st.session_state.nomes_filmes[i])

# Função para escrever o arquivo json
def write_json(file_path:str, mdict:dict):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(mdict, f, indent=4, ensure_ascii=False)
        st.success(f"✅ '{mdict['title']}' salvo em: {file_path}")
    except Exception as e:
        st.error(f"Erro ao salvar {mdict['title']}: {e}")

# Quando clicar em "Pesquisar"
if pesquisar:
    pasta_destino = 'jsons_movies'
    os.makedirs(pasta_destino, exist_ok=True)
    st.success(f"Pasta '{pasta_destino}' verificada/criada.")

    for nome_filme in st.session_state.nomes_filmes:
        if not nome_filme.strip():
            st.warning("Campo de filme vazio ignorado.")
            continue

        # Buscar ID do filme
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={nome_filme}"
        search_resp = requests.get(search_url).json()

        if not search_resp.get("results"):
            st.error(f"❌ Filme '{nome_filme}' não encontrado.")
            continue

        id = search_resp["results"][0]["id"]

        # Buscar detalhes e créditos
        movie = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}").json()
        credits = requests.get(f"https://api.themoviedb.org/3/movie/{id}/credits?api_key={API_KEY}").json()

        diretores = [p['name'] for p in credits['crew'] if p['job'] == 'Director']
        produtores = [p['name'] for p in credits['crew'] if p['job'] == 'Producer']
        roteirista = [p['name'] for p in credits['crew'] if p['job'] == 'Writer']
        atores = [a['name'] for a in credits['cast'][:100]]
        colecao = movie['belongs_to_collection']['name'] if movie['belongs_to_collection'] else ''

        movie_dict = {
            "title": movie['title'],
            "genres": movie['genres'],
            "language": movie['original_language'],
            "country": movie['origin_country'][0] if movie.get('origin_country') else '',
            "director": diretores[0] if len(diretores) == 1 else diretores,
            "producer": produtores[0] if len(produtores) == 1 else produtores,
            "writer": roteirista[0] if len(roteirista) == 1 else roteirista,
            "actors": atores,
            "collection": colecao
        }

        caminho_arquivo = os.path.join(pasta_destino, f"{movie_dict['title']}.json")
        # Verificando se os dados recebidos já existem na lista de JSONs
        JSON_PATHS = glob.glob('jsons_movies/*.json')
        if(caminho_arquivo in JSON_PATHS):
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                movie_dict_old = json.load(f)
            if(movie_dict_old!=movie_dict):
                # Escrevendo os dados recebidos em JSON
                write_json(caminho_arquivo, movie_dict)

                # Re-escrevendo o arquivo OWL
                # (Sim, ele escreve do zero. Se eu tiver que arranjar um jeito 
                # de adicionar instâncias dinamicamente, eu tranco o curso)
                cinegraph_file = OWLFile(BASE_FILE)

                for json_entry in JSON_PATHS:
                    with open(json_entry, 'r') as file:
                        new_info = json.load(file)
                        cinegraph_file.addEntry(new_info)
        
                cinegraph_file.write(OUTPUT_FILE)
        else:
            write_json(caminho_arquivo, movie_dict)
            
            # Nesse aqui eu só adiciono o filme novo mesmo
            cinegraph_file = OWLFile(OUTPUT_FILE)
            cinegraph_file.addEntry(movie_dict)
            cinegraph_file.write(OUTPUT_FILE)            
