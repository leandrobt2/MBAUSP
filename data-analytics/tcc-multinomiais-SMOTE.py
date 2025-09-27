#%% Installing necessary packages
! pip install pandas
! pip install numpy
! pip install openpyxl
! pip install xgboost
! pip install imblearn
! pip install tabulate
! pip install scikit-learn

#############################################################################
#                  REGRESSÃO LOGÍSTICA MULTINOMIAL - SINDICATOS             #
#############################################################################
#%% Importing necessary libraries
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from imblearn.over_sampling import SMOTE
from collections import Counter

#%% Load data
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
merged.reset_index(drop=True, inplace=True)

# Format CNAE fields
merged['cnae'] = merged['cnae'].astype(str).str.replace('-', '').str.replace('.', '').str.replace('/','').str[:8]
merged['cnae2'] = merged['cnae2'].astype(str).str.replace('-', '').str.replace('.', '').str.replace('/','').str[:7]
merged['cnae2'] = merged['cnae2'].replace('Não inf', np.nan)

# Clean city and union names
for col in ['city', 'union']:
    merged[col] = merged[col].astype(str).str.normalize('NFD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    merged[col] = merged[col].str.upper().str.strip()

# Standardize union names
merged['union'] = merged['union'].astype(str).str.replace('SINDICATO DOS CAÇA-FANTASMAS (Não atravesse os feixes!)', 'SINDICATO DOS CAÇA-FANTASMAS')

#%% Encode union as categorical
merged['union_id'] = merged['union'].astype('category').cat.codes

# Filter classes with at least 10 samples
counts = merged['union_id'].value_counts()
merged_filtered = merged[merged['union_id'].isin(counts[counts >= 10].index)]

X = merged_filtered[['city','cnae']]
y = merged_filtered['union']

# One-hot encoding
encoder = OneHotEncoder(drop='first')
X_enc = encoder.fit_transform(X)
feature_names = encoder.get_feature_names_out(['city','cnae'])

#smote = SMOTE(sampling_strategy=0.5, random_state=42)
counts = Counter(y)
print("Distribuição original:", counts)

# Definir meta de amostras para cada classe
# Por exemplo, cada classe terá no máximo 1.000 amostras
target_counts = {cls: min(counts[cls] * 2, 1000) for cls in counts}

print("Target counts para SMOTE:", target_counts)

smote = SMOTE(sampling_strategy=target_counts, random_state=42)
X_res, y_res = smote.fit_resample(X_enc, y)

print(f"Tamanho original: {X.shape[0]}, após SMOTE: {X_res.shape[0]}")

#%% Train multinomial logistic regression
X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.3, random_state=42, stratify=y_res
)

clf = LogisticRegression(
    multi_class='multinomial',
    solver='lbfgs',
    max_iter=500
)
clf.fit(X_train, y_train)

# Coefficients and intercepts
coef_df = pd.DataFrame(clf.coef_, columns=feature_names, index=clf.classes_)
intercept_df = pd.DataFrame(clf.intercept_, index=clf.classes_, columns=['intercept'])

print("Coeficientes por classe:\n", coef_df)
print("\nInterceptos por classe:\n", intercept_df)

#%% Prediction
y_pred = clf.predict(X_test)

acc = accuracy_score(y_test, y_pred)
print("Accuracy:", acc)

report = classification_report(y_test, y_pred, digits=4)
print("\nClassification Report:\n", report)

# Macro averages
macro_precision = precision_score(y_test, y_pred, average='macro')
macro_recall    = recall_score(y_test, y_pred, average='macro')
macro_f1        = f1_score(y_test, y_pred, average='macro')

# Weighted averages
weighted_precision = precision_score(y_test, y_pred, average='weighted')
weighted_recall    = recall_score(y_test, y_pred, average='weighted')
weighted_f1        = f1_score(y_test, y_pred, average='weighted')

print("\nMacro Avg: Precision:", macro_precision)
print("Macro Avg: Recall:", macro_recall)
print("Macro Avg: F1-score:", macro_f1)

print("\nWeighted Avg: Precision:", weighted_precision)
print("Weighted Avg: Recall:", weighted_recall)
print("Weighted Avg: F1-score:", weighted_f1)

# %%
