
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from io import StringIO
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models import Producao, Processamento, Comercializacao
from unidecode import unidecode

DOWNLOAD_BASE = "http://vitibrasil.cnpuv.embrapa.br/"
ABAS = {
    "producao": "opt_02",
    "processamento": "opt_03",
    "comercializacao": "opt_04"
}

TIPOS_PALAVRAS = {
    "producao": ["producao"],
    "comercializacao": ["comercio", "comercializacao"],
    "processamento": ["processa"]
}

def fetch_dados_embrapa(tipo: str):
    try:
        if tipo not in ABAS:
            return {"erro": f"Tipo '{tipo}' inválido. Opções disponíveis: {list(ABAS.keys())}"}

        url = f"{DOWNLOAD_BASE}index.php?opcao={ABAS[tipo]}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        matches = []
        for link in links:
            texto = unidecode(link.text.lower())
            href = unidecode(link["href"].lower())
            if ".csv" in href:
                for palavra in TIPOS_PALAVRAS[tipo]:
                    if palavra in texto or palavra in href:
                        matches.append(link)

        if not matches:
            return {"erro": f"Nenhum arquivo .csv compatível encontrado para {tipo}"}

        arquivo = matches[0]
        url_download = DOWNLOAD_BASE + arquivo["href"]
        file_response = requests.get(url_download)
        df = pd.read_csv(StringIO(file_response.content.decode("latin1")), sep=";")
        df.columns = [col.strip() for col in df.columns]

        if tipo in ["producao", "comercializacao"]:
            id_vars = ["id", "control"]
            possiveis_colunas_produto = ["produto", "Produto"]

            for col in possiveis_colunas_produto:
                if col in df.columns:
                    id_vars.append(col)
                    break
            else:
                return {"erro": "Nenhuma coluna de produto encontrada no arquivo."}

            df = pd.melt(df, id_vars=id_vars, var_name="ano", value_name="quantidade")
            df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.dropna(subset=["quantidade"])
            df["ano"] = df["ano"].astype(int)
            salvar_generico(df, tipo)

        elif tipo == "processamento":
            df = pd.melt(
                df,
                id_vars=["id", "control", "cultivar"],
                var_name="ano",
                value_name="quantidade"
            )
            df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.dropna(subset=["quantidade"])
            df["ano"] = df["ano"].astype(int)
            salvar_generico(df, tipo)

        registros = df.head(100).to_dict(orient="records")
        def clean_json(data):
            for row in data:
                for k, v in row.items():
                    if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                        row[k] = None
            return data

        return {
            "arquivo": arquivo.text.strip(),
            "url_download": url_download,
            "registros": clean_json(registros)
        }

    except Exception as e:
        return {"erro": str(e)}

def salvar_generico(df: pd.DataFrame, tipo: str):
    session = SessionLocal()
    for _, row in df.iterrows():
        try:
            ano = int(row.get("ano", 0))
            id_original = int(row.get("id", 0))
            control = str(row.get("control", ""))

            if tipo == "producao":
                exists = session.query(Producao).filter_by(id_original=id_original, ano=ano).first()
                if not exists:
                    registro = Producao(
                        id_original=id_original,
                        control=control,
                        produto=str(row.get("produto", row.get("Produto", ""))),
                        ano=ano,
                        producao_toneladas=float(row.get("quantidade", 0.0))
                    )
                    session.add(registro)

            elif tipo == "comercializacao":
                exists = session.query(Comercializacao).filter_by(id_original=id_original, ano=ano).first()
                if not exists:
                    registro = Comercializacao(
                        id_original=id_original,
                        control=control,
                        produto=str(row.get("produto", row.get("Produto", ""))),
                        ano=ano,
                        volume_comercializado=float(row.get("quantidade", 0.0))
                    )
                    session.add(registro)

            elif tipo == "processamento":
                exists = session.query(Processamento).filter_by(id_original=id_original, ano=ano).first()
                if not exists:
                    registro = Processamento(
                        id_original=id_original,
                        control=control,
                        cultivar=str(row.get("cultivar", "")),
                        ano=ano,
                        volume_processado_litros=float(row.get("quantidade", 0.0))
                    )
                    session.add(registro)

        except Exception:
            continue
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()
