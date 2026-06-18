import streamlit as st
import pandas as pd
import io

# 1. Configuração Inicial da Página Web
st.set_page_config(
    page_title="Portal RPA - Tratatamento relatorio SAP",
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
aba_me2n, aba_mb51 = st.tabs(["📋 Relatório ME2N", "📦 Relatório MB51"])

# ==============================================================================
# ABAS DE TRATAMENTO
# ==============================================================================

# --- ABA 1: ME2N ---
with aba_me2n:
    st.header("Tratamento do Relatório ME2N")
    st.info("O sistema irá filtrar a coluna 'a ser fornecida (quantidade)' removendo valores menores ou iguais a 0.")
    
    ficheiro_me2n = st.file_uploader("Selecione o ficheiro ME2N (.xlsx ou .xls)", type=["xlsx", "xls"], key="me2n")
    
    if ficheiro_me2n is not None:
        try:
            df_me2n = pd.read_excel(ficheiro_me2n)
            
            # Limpa espaços em branco no começo e no final de todos os nomes de colunas
            df_me2n.columns = df_me2n.columns.str.strip()
            
            # Coloque aqui exatamente como a coluna se chama (cuidado com acentos)
            coluna_filtro = 'a ser fornecida (quantidade)'
            
            if coluna_filtro in df_me2n.columns:
                df_me2n = tratar_coluna_numerica(df_me2n, coluna_filtro)
                df_me2n_tratado = df_me2n[df_me2n[coluna_filtro] > 0]
                
                st.success(f"Sucesso! Linhas originais: {len(df_me2n)} | Linhas após filtro: {len(df_me2n_tratado)}")
                st.dataframe(df_me2n_tratado.head(10), use_container_width=True)
                
                buffer = io.BytesIO()
                df_me2n_tratado.to_excel(buffer, index=False)
                
                st.download_button(
                    label="📥 Transferir ME2N Tratado",
                    data=buffer.getvalue(),
                    file_name="ME2N_Tratado.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.error(f"Erro: A coluna '{coluna_filtro}' não foi encontrada.")
                # ISSO AQUI VAI TE SALVAR: Mostra no site as colunas que o Pandas está enxergando
                st.warning("Estas foram as colunas que o sistema conseguiu ler do seu arquivo. Verifique se o nome está diferente ou se o SAP colocou linhas vazias no topo:")
                st.write(df_me2n.columns.tolist())
                
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o ficheiro: {e}")

# --- ABA 2: MB51 ---
with aba_mb51:
    st.header("Tratamento do Relatório MB51 (Tabela Dinâmica)")
    st.info("O sistema irá consolidar os dados agrupando por Centro, Material e Texto breve.")
    
    ficheiro_mb51 = st.file_uploader("Selecione o ficheiro MB51 (.xlsx ou .xls)", type=["xlsx", "xls"], key="mb51")
    
    if ficheiro_mb51 is not None:
        try:
            df_mb51 = pd.read_excel(ficheiro_mb51)
            df_mb51.columns = df_mb51.columns.str.strip()
            
            # Definindo as 3 colunas exatas da sua imagem para agrupar
            colunas_agrupamento = ['Centro', 'Material', 'Texto breve material']
            col_values = 'Quantidade' # Confirme se o nome da coluna de valor é esse mesmo
            
            # Verifica se todas as colunas necessárias existem no arquivo
            colunas_existem = all(coluna in df_mb51.columns for coluna in colunas_agrupamento + [col_values])
            
            if colunas_existem:
                # Trata os números gigantes e a pontuação para evitar o erro "1E+07"
                df_mb51 = tratar_coluna_numerica(df_mb51, col_values)
                
                # Tabela dinâmica com as 3 colunas
                df_mb51_dinamica = pd.pivot_table(
                    df_mb51,
                    values=col_values,
                    index=colunas_agrupamento,
                    aggfunc='sum'
                ).reset_index()
                
                # Renomeia a coluna final para ficar igual à sua imagem
                df_mb51_dinamica.rename(columns={col_values: 'Soma de Quantidade'}, inplace=True)
                
                st.success("Tabela dinâmica gerada com sucesso!")
                
                # Exibe formatado no site sem a notação científica
                st.dataframe(df_mb51_dinamica.style.format({'Soma de Quantidade': '{:.3f}'}), use_container_width=True)
                
                buffer = io.BytesIO()
                # Salva no Excel. O Pandas cuidará para que fique no formato numérico correto.
                df_mb51_dinamica.to_excel(buffer, index=False)
                
                st.download_button(
                    label="📥 Transferir MB51 (Tabela Dinâmica)",
                    data=buffer.getvalue(),
                    file_name="MB51_Tratado.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.error("Erro: Uma das colunas (Centro, Material, Texto breve material ou Quantidade) não foi encontrada.")
                st.write("Colunas encontradas no arquivo:", df_mb51.columns.tolist())
                
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o ficheiro: {e}")
