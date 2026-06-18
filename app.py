import streamlit as st
import pandas as pd
import io

# 1. Configuração Inicial da Página Web
st.set_page_config(
    page_title="Portal RPA - Automação SAP",
    page_icon="📊",
    layout="wide"
)

# Função auxiliar para limpar e converter colunas numéricas do SAP
def tratar_coluna_numerica(df, nome_coluna):
    if nome_coluna in df.columns:
        # Converte para string para garantir que podemos manipular o texto
        df[nome_coluna] = df[nome_coluna].astype(str)
        # Remove pontos de milhar e substitui a vírgula decimal por ponto
        df[nome_coluna] = df[nome_coluna].str.replace('.', '', regex=False)
        df[nome_coluna] = df[nome_coluna].str.replace(',', '.', regex=False)
        df[nome_coluna] = df[nome_coluna].str.strip()
        # Converte para número real (float), transformando erros em NaN e depois em 0
        df[nome_coluna] = pd.to_numeric(df[nome_coluna], errors='coerce').fillna(0)
    return df

# Título Principal
st.title("⚙️ Portal RPA - Tratamento de Relatórios SAP")
st.write("Carregue os ficheiros extraídos do SAP para realizar o tratamento automático instantâneo.")

# Criar as abas para organizar o site de forma limpa
aba_me2n, aba_mb51, aba_terceira = st.tabs(["📋 Relatório ME2N", "📦 Relatório MB51"])

# ==============================================================================
# ABAS DE TRATAMENTO
# ==============================================================================

# --- ABA 1: ME2N ---
with aba_me2n:
    st.header("Tratamento do Relatório ME2N")
    st.info("O sistema irá filtrar a coluna 'A ser fornecida (quantidade)' removendo valores menores ou iguais a 0.")
    
    ficheiro_me2n = st.file_uploader("Selecione o ficheiro ME2N (.xlsx ou .xls)", type=["xlsx", "xls"], key="me2n")
    
    if ficheiro_me2n is not None:
        try:
            df_me2n = pd.read_excel(ficheiro_me2n)
            coluna_filtro = 'A ser fornecida (quantidade)'
            
            # Verifica se a coluna existe (ignora maiúsculas/minúsculas e espaços extras para evitar erros)
            df_me2n.columns = df_me2n.columns.str.strip()
            
            if coluna_filtro in df_me2n.columns:
                # Trata a formatação dos números antes de filtrar
                df_me2n = tratar_coluna_numerica(df_me2n, coluna_filtro)
                
                # Aplica o filtro (mantém apenas maior que 0)
                df_me2n_tratado = df_me2n[df_me2n[coluna_filtro] > 0]
                
                st.success(f"Sucesso! Linhas originais: {len(df_me2n)} | Linhas após filtro: {len(df_me2n_tratado)}")
                
                # Visualização prévia dos dados tratados
                st.dataframe(df_me2n_tratado.head(10), use_container_width=True)
                
                # Preparar para download
                buffer = io.BytesIO()
                df_me2n_tratado.to_excel(buffer, index=False)
                
                st.download_button(
                    label="📥 Transferir ME2N Tratado",
                    data=buffer.getvalue(),
                    file_name="ME2N_Tratado.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.error(f"Erro: A coluna '{coluna_filtro}' não foi encontrada no ficheiro carregado. Verifique o cabeçalho.")
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o ficheiro: {e}")

# --- ABA 2: MB51 ---
with aba_mb51:
    st.header("Tratamento do Relatório MB51 (Tabela Dinâmica)")
    st.info("O sistema irá consolidar os dados brutos criando um resumo agrupado (Tabela Dinâmica).")
    
    ficheiro_mb51 = st.file_uploader("Selecione o ficheiro MB51 (.xlsx ou .xls)", type=["xlsx", "xls"], key="mb51")
    
    if ficheiro_mb51 is not None:
        try:
            df_mb51 = pd.read_excel(ficheiro_mb51)
            df_mb51.columns = df_mb51.columns.str.strip()
            
            # !!! AJUSTE AQUI OS NOMES REAIS DAS SUAS COLUNAS DO MB51 !!!
            col_index = 'Material'      # Coluna que vai ficar nas linhas
            col_index = 'Centro'      # Coluna que vai ficar nas linhas
            col_index = 'Texto breve material'      # Coluna que vai ficar nas linhas
            col_values = 'Quantidade'    # Coluna que vai ser somada
            
            if col_index in df_mb51.columns and col_values in df_mb51.columns:
                # Trata a coluna de quantidade
                df_mb51 = tratar_coluna_numerica(df_mb51, col_values)
                
                # Criação da tabela dinâmica (Agrupamento por Material somando a Quantidade)
                df_mb51_dinamica = pd.pivot_table(
                    df_mb51,
                    values=col_values,
                    index=[col_index],
                    aggfunc='sum'
                ).reset_index()
                
                st.success("Tabela dinâmica gerada com sucesso!")
                st.dataframe(df_mb51_dinamica, use_container_width=True)
                
                # Preparar para download
                buffer = io.BytesIO()
                df_mb51_dinamica.to_excel(buffer, index=False)
                
                st.download_button(
                    label="📥 Transferir MB51 (Tabela Dinâmica)",
                    data=buffer.getvalue(),
                    file_name="MB51_Tratada.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.error(f"Verifique se as colunas '{col_index}' e '{col_values}' existem no seu relatório MB51.")
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o ficheiro: {e}")
