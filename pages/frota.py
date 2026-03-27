import streamlit as st
import pandas as pd
from src.transform import processar_faturamento_frota

st.set_page_config(page_title="Faturamento Frota", layout="wide", initial_sidebar_state="collapsed")

# planilhas externas

df_rh = pd.read_csv("data/reference/quadro_colaboradores_ativos.csv", sep=None, engine='python', encoding='utf-8-sig')
df_frota = pd.read_csv("data/reference/frota_ativa.csv", sep=None, engine='python', encoding='utf-8-sig')

# upload, validação entre csv e xlsx
relatorio_localiza = st.file_uploader("Arraste aqui o Relatório Localiza (.csv ou .xlsx)", type=["csv", "xlsx"])

if relatorio_localiza:
    if relatorio_localiza.name.endswith('.csv'):
        df_fatura = pd.read_csv(relatorio_localiza, encoding='utf-8-sig')
    else:
        df_fatura = pd.read_excel(relatorio_localiza)
    
# chama a função processar_faturamento_frota do transform.py
    df_final = processar_faturamento_frota(df_fatura, df_frota, df_rh)

    st.divider()

# filtros

    col_servico = [c for c in df_final.columns if 'serviço' in c.lower()]
            
    if col_servico:
        nome_col_serv = col_servico[0]
        opcoes = ["Todos"] + list(df_final[nome_col_serv].unique())
        filtro = st.selectbox("Filtrar por Serviço:", opcoes)
                
        df_relatorio = df_final if filtro == "Todos" else df_final[df_final[nome_col_serv] == filtro]
            
    st.dataframe(df_relatorio, use_container_width=True, hide_index=True)

    # botões de download
            
    # informativo do que o usuário está baixando
    if filtro != "Todos":
        st.info(f"Os downloads abaixo (Relatório e Coupa) estão filtrados por: **{filtro}**")
            
    c1, c2, c3 = st.columns(3)
            
    with c1:
        # download do relatório de faturamento em csv
        st.download_button("Relatório Faturamento", df_relatorio.to_csv(index=False).encode('utf-8'), f"faturamento_{filtro.lower()}.csv")

    with c2:
        # relatório de reclassificação no padrão do final, em progresso
        reclassificao = df_final[df_final['obs_reclass'] == "Sim (Reclassificar)"] #filtra um novo database só com as que vão reclassificar
        st.download_button("Formulário Reclassificação", reclassificao.to_csv(index=False).encode('utf-8'), "reclassificacao_geral.csv",)
            
    with c3:
        # planilha modelo para subir no Coupa na hora do rateio
        valores = [c for c in df_relatorio.columns if 'valor' in c.lower()]
                
        if valores:
            col_valor = valores[0]
            coupa_filtrado = df_relatorio[['cc_lancamento', col_valor]].groupby('cc_lancamento').sum().reset_index()
                    
        st.download_button("Rateio Coupa", coupa_filtrado.to_csv(index=False).encode('utf-8'), f"template_coupa_{filtro.lower()}.csv")
