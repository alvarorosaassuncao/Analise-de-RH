import streamlit as st
import pandas as pd
import PyPDF2
import docx
import io
import matplotlib.pyplot as plt
import seaborn as sns

# Função para carregar o arquivo CSV
def carregar_csv(file):
    df = pd.read_csv(file)
    return df

# Função para carregar o arquivo Excel
def carregar_excel(file):
    df = pd.read_excel(file)
    return df

# Função para carregar o arquivo PDF
def carregar_pdf(file):
    reader = PyPDF2.PdfFileReader(file)
    texto = ""
    for page in range(reader.numPages):
        texto += reader.getPage(page).extract_text()
    return texto

# Função para carregar o arquivo DOCX
def carregar_docx(file):
    doc = docx.Document(file)
    texto = ""
    for para in doc.paragraphs:
        texto += para.text + "\n"
    return texto

# Função para exibir análises e filtros
def exibir_analises(df):
    st.sidebar.header('Filtros de Análise de RH')
    
    # Filtro por Departamento
    departamentos = df['Departamento'].unique().tolist()
    departamento_selecionado = st.sidebar.selectbox('Selecione o Departamento', ['Todos'] + departamentos)
    if departamento_selecionado != 'Todos':
        df = df[df['Departamento'] == departamento_selecionado]
    
    # Filtro por Cargo
    cargos = df['Cargo'].unique().tolist()
    cargos_selecionados = st.sidebar.multiselect('Selecione os Cargos', cargos, default=cargos)
    
    if not cargos_selecionados:
        st.sidebar.warning('Selecione pelo menos um Cargo para continuar.')
        return
    
    df = df[df['Cargo'].isin(cargos_selecionados)]
    
    # Filtro por CPF
    cpf = st.sidebar.text_input('Digite o CPF')
    if cpf:
        df = df[df['CPF'] == cpf]
    
    # Filtro por Status
    status = df['Status'].unique().tolist()
    status_selecionado = st.sidebar.selectbox('Selecione o Status', ['Todos'] + status)
    if status_selecionado != 'Todos':
        df = df[df['Status'] == status_selecionado]

    # Opção para ocultar/mostrar a tabela
    mostrar_tabela = st.sidebar.checkbox('Mostrar Tabela', value=True)
    if mostrar_tabela:
        st.write('Dados Carregados:')
        st.write(df)

    st.write('Dados Filtrados:')
    st.write(df)

    # Mostrar total de funcionários
    total_funcionarios = len(df)
    st.write(f'### Total de Funcionários: {total_funcionarios}')

    # Exportar dados filtrados
    st.sidebar.download_button(
        label="Exportar Dados Filtrados",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='dados_filtrados.csv',
        mime='text/csv'
    )

    # Análises
    st.write('## Distribuição de Cargos')
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=df['Cargo'].value_counts().index, y=df['Cargo'].value_counts().values, ax=ax, palette='viridis')
    ax.set_xlabel('Cargo')
    ax.set_ylabel('Contagem')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)
    
    st.write('## Status dos Funcionários')
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=df['Status'].value_counts().index, y=df['Status'].value_counts().values, ax=ax, palette='viridis')
    ax.set_xlabel('Status')
    ax.set_ylabel('Contagem')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)
    
    # Análise de Tendências
    if 'Data de Contratação' in df.columns and 'Data de Demissão' in df.columns:
        df['Data de Contratação'] = pd.to_datetime(df['Data de Contratação'])
        df['Data de Demissão'] = pd.to_datetime(df['Data de Demissão'])
        
        st.write('## Tendência de Contratação ao Longo do Tempo')
        df_contratacoes = df.set_index('Data de Contratação').resample('M').size()
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=df_contratacoes, ax=ax)
        ax.set_xlabel('Data de Contratação')
        ax.set_ylabel('Número de Contratações')
        st.pyplot(fig)
        
        st.write('## Tendência de Demissão ao Longo do Tempo')
        df_demissoes = df.set_index('Data de Demissão').resample('M').size()
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=df_demissoes, ax=ax)
        ax.set_xlabel('Data de Demissão')
        ax.set_ylabel('Número de Demissões')
        st.pyplot(fig)

# Criação do dashboard com Streamlit
st.set_page_config(layout="centered")  # Layout intermediário
st.title('Análise de Arquivos de RH')

# Carregar o arquivo
file = st.file_uploader('Carregar arquivo', type=['csv', 'xlsx', 'pdf', 'docx'])

# Mostrar os dados carregados
if file is not None:
    if file.type == 'text/csv':
        df = carregar_csv(file)
        exibir_analises(df)
    elif file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = carregar_excel(file)
        exibir_analises(df)
    elif file.type == 'application/pdf':
        texto = carregar_pdf(file)
        st.write('Dados Carregados (PDF):')
        st.write(texto)
    elif file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        texto = carregar_docx(file)
        st.write('Dados Carregados (DOCX):')
        st.write(texto)
