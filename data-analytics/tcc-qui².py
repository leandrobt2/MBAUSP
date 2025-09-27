#%% Installing necessary packages
! pip install pandas
! pip install numpy

#%% Load data
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

# Exemplo: carregar a mesma base unificada
dados_feco = pd.read_csv("./dataset/fake-alpha.csv")
dados_leandro_4 = pd.read_csv("./dataset/fake-alpha2.csv")
dados_leandro_6 = pd.read_csv("./dataset/fake-alpha3.csv")

#%% Data wrangling

# Selecting relevant columns from each dataset
feco_cols = ['Column1','Column2', 'Column3', 'Column32', 'Column5', 'Column4']
leandro_4_cols = ['EmpresaID','Documento', 'CnaePrincipal', 'CnaeSecundario', 'Municipio', 'SindicatoVinculoGestao']
leandro_6_cols = ['EmpresaID','Documento', 'CnaePrincipal', 'CnaeSecundario', 'Municipio', 'SindicatoVinculoGestao']

# Dropping irrelevant columns and renaming them for consistency
df_feco = dados_feco.drop(columns=[col for col in dados_feco.columns if col not in feco_cols])
df_leandro_4 = dados_leandro_4.drop(columns=[col for col in dados_leandro_4.columns if col not in leandro_4_cols])
df_leandro_6 = dados_leandro_6.drop(columns=[col for col in dados_leandro_6.columns if col not in leandro_6_cols])

# Renaming columns for consistency across datasets
df_feco = df_feco.rename(columns={'Column1': 'id','Column2':'CNPJ', 'Column3': 'cnae', 'Column32': 'cnae2', 'Column5': 'city', 'Column4': 'union'})
df_leandro_4 = df_leandro_4.rename(columns={'EmpresaID': 'id', 'Documento':'CNPJ','CnaePrincipal': 'cnae', 'CnaeSecundario': 'cnae2', 'Municipio': 'city', 'SindicatoVinculoGestao': 'union'})
df_leandro_6 = df_leandro_6.rename(columns={'EmpresaID': 'id', 'Documento':'CNPJ','CnaePrincipal': 'cnae', 'CnaeSecundario': 'cnae2', 'Municipio': 'city', 'SindicatoVinculoGestao': 'union'})

# Concatenate vertically (stack)
merged = pd.concat([df_feco, df_leandro_4, df_leandro_6], axis=0, ignore_index=True)

# Remove duplicates based on 'id' and 'CNPJ'
merged = merged.drop_duplicates(subset=['id', 'CNPJ'])
# Reset index after dropping duplicates
merged.reset_index(drop=True, inplace=True)

# Fomat cnae field, remove "-" and "."" and get first 7 characteres
merged['cnae'] = merged['cnae'].astype(str).str.replace('-', '').str.replace('.', '').str.replace('/','').str[:8]
merged['cnae2'] = merged['cnae2'].astype(str).str.replace('-', '').str.replace('.', '').str.replace('/','').str[:7]
merged['cnae2'] = merged['cnae2'].replace('Não inf', np.nan)

# remove all tildes from city names and convert to uppercase and trailing ending spaces
for col in ['city', 'union']:
    merged[col] = merged[col].astype(str).str.normalize('NFD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    merged[col] = merged[col].str.upper().str.strip()

# format union field
merged['union'] = merged['union'].astype(str).str.replace('SINDICATO DOS CAÇA-FANTASMAS (Não atravesse os feixes!)', 'SINDICATO DOS CAÇA-FANTASMAS')

col1 = "union" # exemplo
col2 = "city"  # exemplo

# Criar tabela de contingência
contingencia = pd.crosstab(merged[col1], merged[col2])

# Rodar qui-quadrado
chi2, p, dof, expected = chi2_contingency(contingencia)

print("=== Teste do Qui-quadrado ===")
print(f"Valor Qui²: {chi2:.4f}")
print(f"Graus de liberdade: {dof}")
print(f"p-valor: {p:.12f}")

if p < 0.05:
    print("🔎 Existe associação estatisticamente significativa entre as variáveis!")
else:
    print("ℹ️ Não há evidência de associação significativa entre as variáveis.")
# %%
