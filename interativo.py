# %% [markdown]
# # Processamento Interativo de Dados Vitibrasil

# %% [markdown]
# ## Etapa 1: Configurações Iniciais

# %%
import pandas as pd
import numpy as np
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models import Importacao, Exportacao
import os

# Definições
TIPO = "importacao"  # ou "exportacao"
ARQUIVO_CSV = "ImpVinhos.csv" if TIPO == "importacao" else "expvinho.csv"
CAMINHO_CSV = os.path.expanduser(f"~/Downloads/{ARQUIVO_CSV}")

# %% [markdown]
# ## Etapa 2: Carregamento do CSV Local

# %%
# Carregar CSV com codificação correta
try:
    df = pd.read_csv(CAMINHO_CSV, sep="\t", encoding="utf-8-sig")
    print(f"✅ Arquivo {ARQUIVO_CSV} carregado com sucesso!")
    
    # Renomear colunas e converter ID para inteiro
    df.rename(columns={"Id": "id", "País": "pais"}, inplace=True)
    df.columns = [col.lower() for col in df.columns]
    df["id"] = df["id"].astype(int)
    
    print(f"📊 Dimensões do DataFrame: {df.shape[0]} linhas, {df.shape[1]} colunas")
    display(df.head())
except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {CAMINHO_CSV}")
    raise

# %% [markdown]
# ## Etapa 3: Processamento de Dados

# %%
# Transformar dados do formato wide para long
df_long = pd.DataFrame()
colunas = df.columns

print("🔄 Processando colunas:")
for i in range(2, len(colunas), 2):
    ano = colunas[i]
    print(f" → Ano: {ano}")
    
    temp = pd.DataFrame({
        "pais": df[colunas[1]],
        "ano": int(ano),
        "quantidade": pd.to_numeric(df[colunas[i]], errors="coerce"),
        "valor_usd": pd.to_numeric(df[colunas[i + 1]], errors="coerce")
    })
    df_long = pd.concat([df_long, temp], ignore_index=True)

# Limpeza final
df_long = df_long.dropna(subset=["quantidade", "valor_usd"])
df_long = df_long.replace([np.inf, -np.inf], np.nan).dropna()
df_long[["quantidade", "valor_usd"]] = df_long[["quantidade", "valor_usd"]].astype(float)

print(f"\n📊 Total de registros processados: {len(df_long)}")
display(df_long.head())

# %% [markdown]
# ## Etapa 4: Salvamento no Banco de Dados

# %%
# Confirmar salvamento
if input("💾 Confirmar salvamento no banco (s/n): ").lower() == "s":
    session = SessionLocal()
    registros_inseridos = 0
    
    print("\n🔄 Iniciando inserção de registros:")
    for idx, row in df_long.iterrows():
        try:
            pais = str(row["pais"]).strip()
            ano = int(row["ano"])
            
            if TIPO == "importacao":
                if not session.query(Importacao).filter_by(pais=pais, ano=ano).first():
                    registro = Importacao(**{
                        "pais": pais,
                        "ano": ano,
                        "quantidade": float(row["quantidade"]),
                        "valor_usd": float(row["valor_usd"])
                    })
                    session.add(registro)
                    registros_inseridos += 1
                    
            elif TIPO == "exportacao":
                if not session.query(Exportacao).filter_by(pais=pais, ano=ano).first():
                    registro = Exportacao(**{
                        "pais": pais,
                        "ano": ano,
                        "quantidade": float(row["quantidade"]),
                        "valor_usd": float(row["valor_usd"])
                    })
                    session.add(registro)
                    registros_inseridos += 1
                    
        except Exception as e:
            print(f"⚠️ Erro na linha {idx}: {str(e)}")
            continue
            
    try:
        session.commit()
        print(f"\n🎉 Salvou {registros_inseridos} novos registros no banco!")
    except IntegrityError as e:
        session.rollback()
        print(f"\n❌ Erro de integridade: {str(e)}")
    finally:
        session.close()
else:
    print("↩️  Operação cancelada")