
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models import Importacao, Exportacao
from unidecode import unidecode

DOWNLOAD_BASE = "http://vitibrasil.cnpuv.embrapa.br/"
ARQUIVOS_ESPECIAIS = {
    "importacao": "ImpVinhos.csv",
    "exportacao": "expvinho.csv"
}
ABAS_ESPECIAIS = {
    "importacao": "opt_05",
    "exportacao": "opt_06"
}

def fetch_dados_import_export(tipo: str):
    try:
        if tipo not in ABAS_ESPECIAIS:
            return {"erro": f"Tipo '{tipo}' inválido. Use 'importacao' ou 'exportacao'."}

        url = f"{DOWNLOAD_BASE}index.php?opcao={ABAS_ESPECIAIS[tipo]}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        arquivo_desejado = ARQUIVOS_ESPECIAIS[tipo].lower()
        links = soup.find_all("a", href=True)
        arquivos = [link for link in links if arquivo_desejado in unidecode(link["href"].lower())]

        if not arquivos:
            return {"erro": f"Arquivo {arquivo_desejado} não encontrado na página."}

        url_download = DOWNLOAD_BASE + arquivos[0]["href"]
        file_response = requests.get(url_download)

        # Lê o CSV com codificação correta
        df = pd.read_csv(StringIO(file_response.content.decode("utf-8-sig")), sep="\t")
        
        # Renomeia colunas para alinhar com o modelo Pydantic
        df.rename(columns={"Id": "id", "País": "pais"}, inplace=True)
        df.columns = [col.lower() for col in df.columns]  # Garante minúsculas
        df["id"] = df["id"].astype(int)

        # Valida colunas críticas
        if "id" not in df.columns:
            return {"erro": "Coluna 'id' não encontrada no CSV"}

        registros = processar_tabela_ano_duplo(df, tipo)
        
        return {
            "arquivo": arquivos[0].text.strip(),
            "url_download": url_download,
            "registros": registros[:100]
        }

    except Exception as e:
        return {"erro": str(e)}
    

def processar_tabela_ano_duplo(df: pd.DataFrame, tipo: str):
    try:
        df_long = pd.DataFrame()
        colunas = df.columns

        for i in range(2, len(colunas), 2):
            ano = colunas[i]
            temp = pd.DataFrame({
                "id": df[colunas[0]],
                "pais": df[colunas[1]],
                "ano": int(ano),
                "quantidade": pd.to_numeric(df[colunas[i]], errors="coerce"),
                "valor_usd": pd.to_numeric(df[colunas[i + 1]], errors="coerce")
            })
            df_long = pd.concat([df_long, temp], ignore_index=True)

        df_long = df_long.dropna(subset=["quantidade", "valor_usd"])
        df_long = df_long.replace([float("inf"), float("-inf")], pd.NA)
        df_long = df_long.dropna()
        salvar_import_export(df_long, tipo)
        return df_long.to_dict(orient="records")
    except Exception as e:
        return [{"erro": str(e)}]

def salvar_import_export(df: pd.DataFrame, tipo: str):
    session = SessionLocal()
    for _, row in df.iterrows():
        try:
            pais = str(row.get("pais", "")).strip()
            ano = int(row.get("ano", 0))

            if tipo == "importacao":
                exists = session.query(Importacao).filter_by(pais=pais, ano=ano).first()
                if not exists:
                    registro = Importacao(
                        pais=pais,
                        ano=ano,
                        quantidade=float(row.get("quantidade", 0.0)),
                        valor_usd=float(row.get("valor_usd", 0.0))
                    )
                    session.add(registro)

            elif tipo == "exportacao":
                exists = session.query(Exportacao).filter_by(pais=pais, ano=ano).first()
                if not exists:
                    registro = Exportacao(
                        pais=pais,
                        ano=ano,
                        quantidade=float(row.get("quantidade", 0.0)),
                        valor_usd=float(row.get("valor_usd", 0.0))
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
