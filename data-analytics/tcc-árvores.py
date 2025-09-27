#%% Installing necessary packages
! pip install pandas
! pip install numpy
! pip install openpyxl
! pip install xgboost
! pip install imblearn

#%% Importing necessary libraries
import pandas as pd
import numpy as np
import openpyxl as px
# Importing sklearn libraries
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import GridSearchCV
# Importing XGBoost
from xgboost import XGBClassifier
# Importing visualization libraries
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
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

# #%% Print Fronts
# import matplotlib.font_manager
# from IPython.core.display import HTML

# def make_html(fontname):
#     return "<p>{font}: <span style='font-family:{font}; font-size: 24px;'>{font}</p>".format(font=fontname)

# code = "\n".join([make_html(font) for font in sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))])

# HTML("<div style='column-count: 2;'>{}</div>".format(code))

#%% Data visualization

import matplotlib.pyplot as plt
import matplotlib as mpl

# Use generic sans-serif; Arial if available
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Helvetica']
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['axes.facecolor'] = 'white'

min_samples2 = 10
counts = merged['union'].value_counts()
valid_unions = counts[counts >= min_samples2].index

data = merged[merged['union'].isin(valid_unions)]

def format_ax(ax, xlabel, ylabel):
    # Remove grid
    ax.grid(False)

    # Keep only bottom and left spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set line style for main axes
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_edgecolor('black')
    ax.spines['left'].set_edgecolor('black')

    # Axis labels style
    ax.set_xlabel(xlabel, fontsize=11, color='black')
    ax.set_ylabel(ylabel, fontsize=11, color='black')

    # Remove chart title
    ax.set_title('')

    # Remove x-axis tick labels
    ax.set_xticks([])

# 1) Unions
union2 = data['union'].value_counts(normalize=True).reset_index()
union2.columns = ['union', 'percentage']
fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
ax.bar(union2['union'], union2['percentage'], color='#a5a5a5')
format_ax(ax, xlabel='Sindicato', ylabel='Porcentagem')
plt.tight_layout()

# 2) Cities
city_counts = data['city'].value_counts(normalize=True).reset_index()
city_counts.columns = ['city', 'percentage']
fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
ax.bar(city_counts['city'], city_counts['percentage'], color='#a5a5a5')
format_ax(ax, xlabel='Cidade', ylabel='Porcentagem')
plt.tight_layout()

# 3) Cities without main
city_counts2 = data['city'].value_counts(normalize=True).reset_index()
city_counts2.columns = ['city', 'percentage']
city_counts2 = city_counts2.iloc[1:].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
ax.bar(city_counts2['city'], city_counts2['percentage'], color='#a5a5a5')
format_ax(ax, xlabel='Cidade (sem a principal)', ylabel='Porcentagem')
plt.tight_layout()

# 4) CNAE
cnaes_counts = data['cnae'].value_counts(normalize=True).reset_index()
cnaes_counts.columns = ['cnae', 'percentage']
fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
ax.bar(cnaes_counts['cnae'], cnaes_counts['percentage'], color='#a5a5a5')
format_ax(ax, xlabel='CNAE', ylabel='Porcentagem')
plt.tight_layout()

plt.show()

#%% Gráfico único: Top 5 sindicatos x Top 10 CNAEs mais comuns (sem legenda e sem rótulos)

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

# Seleciona top 5 sindicatos
top5_unions = merged['union'].value_counts().head(5).index
df_top5 = merged[merged['union'].isin(top5_unions)]

# Top 10 CNAEs considerando todos os sindicatos
top10_cnaes = df_top5['cnae'].value_counts().head(10).index

# Criar matriz de frequências
freq_matrix = []
for union_name in top5_unions:
    counts = df_top5[df_top5['union'] == union_name]['cnae'].value_counts()
    freq_matrix.append([counts.get(cnae, 0) for cnae in top10_cnaes])

freq_matrix = np.array(freq_matrix)

# Definir tons de cinza diferentes
gray_shades = ['#4d4d4d', '#666666', '#808080', '#999999', '#b3b3b3']

# Parâmetros para gráfico de barras agrupadas
x = np.arange(len(top10_cnaes))
width = 0.15

fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')

for i, shade in enumerate(gray_shades):
    ax.bar(x + i*width, freq_matrix[i], width, color=shade)

# Formatação conforme norma
ax.grid(False)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.spines['bottom'].set_visible(True)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_edgecolor('black')
ax.spines['left'].set_edgecolor('black')

# Eixos
ax.set_xlabel("CNAE", fontsize=11, color='black')
ax.set_ylabel("Frequência", fontsize=11, color='black')
ax.set_xticks(x + width*(len(top5_unions)-1)/2)
ax.set_xticklabels(top10_cnaes, rotation=45, ha='right')

# Remover título e legenda
ax.set_title("")

plt.tight_layout()
plt.show()


#%% Random Forest
# --- ENCODING ---
min_samples = 1
counts = merged['union'].value_counts()
valid_unions = counts[counts >= min_samples].index

data = merged[merged['union'].isin(valid_unions)]

le_city = LabelEncoder()
data['city_enc'] = le_city.fit_transform(data['city'])

le_cnae = LabelEncoder()
data['cnae_enc'] = le_cnae.fit_transform(data['cnae'])

le_union = LabelEncoder()
data['union_enc'] = le_union.fit_transform(data['union'])

X = data[['city_enc', 'cnae_enc']]
y = data['union_enc']

# --- TRAIN TEST SPLIT ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42
)

# --- RANDOM FOREST ---
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)

params = rf.get_params()

depths = [estimator.tree_.max_depth for estimator in rf.estimators_]
print(f"Profundidade média: {np.mean(depths)}")

y_pred = rf.predict(X_test)

# --- METRICS ---
print("Random Forest Accuracy:", accuracy_score(y_test, y_pred))
print("Random Forest Macro F1-score:", f1_score(y_test, y_pred, average='macro'))
print(classification_report(y_test, y_pred))


#%% XGBoost

# Fazendo uma cópia do DataFrame original para evitar alterações indesejadas
data = merged.copy()

min_samples = 1
counts = data['union'].value_counts()
valid_unions = counts[counts >= min_samples].index

data = data[data['union'].isin(valid_unions)]

# Convertendo as colunas 'cnae', 'city' e 'union' para string e aplicando LabelEncoder
for col in ['cnae', 'city', 'union']:
    data[col] = data[col].astype(str)  # Garantindo que os dados são strings
    le = LabelEncoder()                # Inicializando o codificador
    data[col] = le.fit_transform(data[col])  # Codificando a coluna com números inteiros

# Salvando os rótulos originais da coluna 'union' para referência posterior
original_union_labels = data['union'].astype(str)

# Separando as features (X) e a variável alvo (y)
X = data[['cnae', 'city']]   # Features: CNAE e cidade codificados
y = original_union_labels    # Alvo: rótulos de sindicato codificados como string

# Contando a quantidade de instâncias por classe
class_counts = y.value_counts()

# Identificando classes que possuem apenas uma instância
single_instance_classes = class_counts[class_counts == 1].index

# Criando uma máscara booleana para manter apenas classes com mais de uma instância
rows_to_keep = ~y.isin(single_instance_classes)

# Filtrando X e y para remover as classes com apenas uma instância
X_filtered = X[rows_to_keep]
y_filtered = y[rows_to_keep]

# Ajustando o LabelEncoder apenas com as classes restantes após o filtro
le_union = LabelEncoder()
le_union.fit(y_filtered)  # Fit com as classes válidas
y_encoded = le_union.transform(y_filtered)  # Transformando os rótulos para valores numéricos

# Dividindo os dados em treino e teste com estratificação para preservar a distribuição das classes
X_train, X_test, y_train, y_test = train_test_split(
    X_filtered,
    y_encoded,
    test_size=0.15,       # 20% para teste
    random_state=42,     # Garantindo reprodutibilidade
    stratify=y_encoded   # Mantendo a proporção das classes
)

# Inicializando o modelo XGBoost para classificação multiclasse
model = XGBClassifier(
    objective='multi:softmax',           # Problema de classificação multiclasse
    eval_metric='mlogloss',              # Métrica de avaliação: log-loss
    use_label_encoder=False,             # Evitando aviso sobre uso do LabelEncoder interno
    random_state=42,                     # Reprodutibilidade
    num_class=len(le_union.classes_)     # Definindo o número de classes
)

# Treinando o modelo com os dados de treinamento
model.fit(X_train, y_train)

# Realizando previsões com o modelo treinado
y_pred = model.predict(X_test)

# # Calculando a acurácia das previsões
acc = accuracy_score(y_test, y_pred)

# # Calculando o F1-score macro (média entre todas as classes)
f1 = f1_score(y_test, y_pred, average='macro')

# Exibindo as métricas de desempenho
print(f"XGBoost Accuracy: {acc:.4f}")
print(f"XGBoost Macro F1-score: {f1:.4f}")

# Gerando o relatório de classificação com os nomes originais das classes
print(classification_report(
     le_union.inverse_transform(y_test),  # Convertendo os rótulos numéricos para strings
     le_union.inverse_transform(y_pred)  # Convertendo as previsões para strings
 ))

# %% XGBoost with Grid Search
# Fazendo uma cópia do DataFrame original para evitar alterações indesejadas
data = merged.copy()

min_samples = 2
counts = data['union'].value_counts()
valid_unions = counts[counts >= min_samples].index

data = data[data['union'].isin(valid_unions)]

# Convertendo as colunas 'cnae', 'city' e 'union' para string e aplicando LabelEncoder
for col in ['cnae', 'city', 'union']:
    data[col] = data[col].astype(str)  # Garantindo que os dados são strings
    le = LabelEncoder()                # Inicializando o codificador
    data[col] = le.fit_transform(data[col])  # Codificando a coluna com números inteiros

# Salvando os rótulos originais da coluna 'union' para referência posterior
original_union_labels = data['union'].astype(str)

# Separando as features (X) e a variável alvo (y)
X = data[['cnae', 'city']]   # Features: CNAE e cidade codificados
y = original_union_labels    # Alvo: rótulos de sindicato codificados como string

# Contando a quantidade de instâncias por classe
class_counts = y.value_counts()

# Identificando classes que possuem apenas uma instância
single_instance_classes = class_counts[class_counts == 1].index

# Criando uma máscara booleana para manter apenas classes com mais de uma instância
rows_to_keep = ~y.isin(single_instance_classes)

# Filtrando X e y para remover as classes com apenas uma instância
X_filtered = X[rows_to_keep]
y_filtered = y[rows_to_keep]

# Ajustando o LabelEncoder apenas com as classes restantes após o filtro
le_union = LabelEncoder()
le_union.fit(y_filtered)  # Fit com as classes válidas
y_encoded = le_union.transform(y_filtered)  # Transformando os rótulos para valores numéricos

# Dividindo os dados em treino e teste com estratificação para preservar a distribuição das classes
X_train, X_test, y_train, y_test = train_test_split(
    X_filtered,
    y_encoded,
    test_size=0.15,       # 20% para teste
    random_state=42,     # Garantindo reprodutibilidade
    stratify=y_encoded   # Mantendo a proporção das classes
)

# Inicializando o modelo XGBoost para classificação multiclasse
model = XGBClassifier(
    objective='multi:softmax',           # Problema de classificação multiclasse
    eval_metric='mlogloss',              # Métrica de avaliação: log-loss
    use_label_encoder=False,             # Evitando aviso sobre uso do LabelEncoder interno
    random_state=42,                     # Reprodutibilidade
    num_class=len(le_union.classes_)     # Definindo o número de classes
)

# Definir a grade de hiperparâmetros
param_grid = {
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'n_estimators': [50, 100, 150],
    'subsample': [0.8, 1],
    'colsample_bytree': [0.8, 1]
}

# Criar o GridSearchCV
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=4,  # ou 5, conforme o tamanho do dataset
    scoring='f1_macro',  # ou 'accuracy'
    n_jobs=-1,  # paralelismo total
    verbose=1
)

# Ajustar o modelo
grid_search.fit(X_train, y_train)

# Exibir os melhores parâmetros e o melhor score
print("Melhores parâmetros:", grid_search.best_params_)
print("Melhor F1-macro:", grid_search.best_score_)

# Avaliar no conjunto de teste
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

# Avaliação
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='macro')

print(f"XGBoost (melhor modelo) Accuracy: {acc:.4f}")
print(f"XGBoost (melhor modelo) Macro F1-score: {f1:.4f}")

# Relatório
print(classification_report(
    y_test,
    y_pred,
    target_names=le_union.classes_
))
# %%

#%% Importações para SMOTE e validação cruzada estratificada
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import StratifiedKFold, cross_val_score

# Preparação dos dados (exemplo Random Forest, mas serve para XGBoost também)

min_samples = 10
counts = merged['union'].value_counts()
valid_unions = counts[counts >= min_samples].index
data = merged[merged['union'].isin(valid_unions)].copy()

# Label Encoding
le_city = LabelEncoder()
data['city_enc'] = le_city.fit_transform(data['city'])

le_cnae = LabelEncoder()
data['cnae_enc'] = le_cnae.fit_transform(data['cnae'])

le_union = LabelEncoder()
data['union_enc'] = le_union.fit_transform(data['union'])

X = data[['city_enc', 'cnae_enc']]
y = data['union_enc']

# --- Estratégia de Sampling para desbalanceamento ---

# Undersampling já feito via remoção de classes muito pequenas (min_samples=40)

#smote = SMOTE(sampling_strategy=0.5, random_state=42)
counts = Counter(y)
print("Distribuição original:", counts)
# Definir meta de amostras para cada classe (menos agressivo)
# Por exemplo, cada classe terá no máximo 2.000 amostras
target_counts = {cls: min(counts[cls] * 2, 1000) for cls in counts}

# Aplicando Oversampling com SMOTE
#smote = SMOTE(random_state=42)
smote = SMOTE(sampling_strategy=target_counts, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

print(f"Tamanho original: {X.shape[0]}, após SMOTE: {X_resampled.shape[0]}")

# --- Validação Cruzada Estratificada ---

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')

# Avaliando com cross_val_score usando f1_macro, que é adequado para dados desbalanceados
scores = cross_val_score(rf, X_resampled, y_resampled, cv=skf, scoring='f1_macro', n_jobs=-1)

print(f"F1-macro com SMOTE (5-fold CV): {scores.mean():.4f} ± {scores.std():.4f}")

# Treinar/testar modelo no conjunto completo com divisão estratificada (para comparação)

X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.15, random_state=42, stratify=y_resampled
)

rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

print("Random Forest Accuracy (com SMOTE):", accuracy_score(y_test, y_pred))
print("Random Forest Macro F1-score (com SMOTE):", f1_score(y_test, y_pred, average='macro'))
print(classification_report(y_test, y_pred, target_names=le_union.classes_))

# --- Para comparação: modelo sem SMOTE (apenas undersampling) ---

X_train_orig, X_test_orig, y_train_orig, y_test_orig = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

rf_orig = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf_orig.fit(X_train_orig, y_train_orig)
y_pred_orig = rf_orig.predict(X_test_orig)

print("Random Forest Accuracy (sem SMOTE):", accuracy_score(y_test_orig, y_pred_orig))
print("Random Forest Macro F1-score (sem SMOTE):", f1_score(y_test_orig, y_pred_orig, average='macro'))
print(classification_report(y_test_orig, y_pred_orig, target_names=le_union.classes_))

#%% Comparação com SMOTE para diferentes algoritmos (Random Forest, XGBoost e XGBoost com GridSearch)
from imblearn.over_sampling import SMOTE

# Preparação dos dados
min_samples = 10
counts = merged['union'].value_counts()
valid_unions = counts[counts >= min_samples].index
data = merged[merged['union'].isin(valid_unions)].copy()

# Label Encoding
le_city = LabelEncoder()
data['city_enc'] = le_city.fit_transform(data['city'])

le_cnae = LabelEncoder()
data['cnae_enc'] = le_cnae.fit_transform(data['cnae'])

le_union = LabelEncoder()
data['union_enc'] = le_union.fit_transform(data['union'])

X = data[['city_enc', 'cnae_enc']]
y = data['union_enc']

counts = Counter(y)
print("Distribuição original:", counts)
# Definir meta de amostras para cada classe (menos agressivo)
# Por exemplo, cada classe terá no máximo 2.000 amostras
target_counts = {cls: min(counts[cls] * 2, 3000) for cls in counts}

# --- Aplicando Oversampling com SMOTE ---
smote = SMOTE(sampling_strategy=target_counts, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

print(f"Tamanho original: {X.shape[0]}, após SMOTE: {X_resampled.shape[0]}")

#smote = SMOTE(random_state=42)
#X_resampled, y_resampled = smote.fit_resample(X, y)
#print(f"[SMOTE] Tamanho original: {X.shape[0]}, após SMOTE: {X_resampled.shape[0]}")

# --- Train/test split com estratificação ---
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.15, random_state=42, stratify=y_resampled
)

def print_metrics(y_true, y_pred, classes, title):
    print(f"\n[{title}]")
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=classes, output_dict=True)
    print(f"Accuracy: {acc:.4f}")
    print(f"Macro Avg - Precision: {report['macro avg']['precision']:.4f}")
    print(f"Macro Avg - Recall: {report['macro avg']['recall']:.4f}")
    print(f"Macro Avg - F1-score: {report['macro avg']['f1-score']:.4f}")
    print(f"Weighted Avg - Precision: {report['weighted avg']['precision']:.4f}")
    print(f"Weighted Avg - Recall: {report['weighted avg']['recall']:.4f}")
    print(f"Weighted Avg - F1-score: {report['weighted avg']['f1-score']:.4f}")

# 1) Random Forest com SMOTE
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
print_metrics(y_test, y_pred, le_union.classes_, "Random Forest + SMOTE")

# 2) XGBoost com SMOTE
xgb_model = XGBClassifier(
    objective='multi:softmax',
    eval_metric='mlogloss',
    use_label_encoder=False,
    random_state=42,
    num_class=len(le_union.classes_)
)
xgb_model.fit(X_train, y_train)
y_pred = xgb_model.predict(X_test)
print_metrics(y_test, y_pred, le_union.classes_, "XGBoost + SMOTE")

# 3) XGBoost com GridSearch + SMOTE
param_grid = {
    'max_depth': [3, 5],
    'learning_rate': [0.05, 0.1],
    'n_estimators': [50, 100],
    'subsample': [0.8, 1],
    'colsample_bytree': [0.8, 1]
}

grid_search = GridSearchCV(
    estimator=XGBClassifier(
        objective='multi:softmax',
        eval_metric='mlogloss',
        use_label_encoder=False,
        random_state=42,
        num_class=len(le_union.classes_)
    ),
    param_grid=param_grid,
    cv=3,
    scoring='f1_macro',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

print(f"\n[XGBoost + GridSearch + SMOTE] Melhores parâmetros: {grid_search.best_params_}")
print_metrics(y_test, y_pred, le_union.classes_, "XGBoost + GridSearch + SMOTE")

# %%
