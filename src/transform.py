import pandas as pd

def processar_faturamento_frota(df_localiza, df_frota, df_rh):
    # padronização de colunas, tirando espaços e colocando tudo em minúsculo para evitar erros de merge
    # strip() remove espaços em branco no início e no fim, lower() coloca tudo em minúsculo
    df_localiza.columns = df_localiza.columns.str.strip().str.lower()
    df_frota.columns = df_frota.columns.str.strip().str.lower()
    df_rh.columns = df_rh.columns.str.strip().str.lower()

    # renomeação das colunas
    df_localiza = df_localiza.rename(columns={'usuário': 'usuario_localiza'})
    df_frota = df_frota.rename(columns={'condutor': 'nome_link'})
    df_rh = df_rh.rename(columns={'nome': 'nome_link', 'c.custo folha': 'centro_custo_final'})

    # nova df com procv entre placa do carro (df_localiza) e funcionário (df_rh)
    df = pd.merge(df_localiza, df_frota, on='placa', how='left')

    # procv entre nova df (df) e centro de custo (df_rh)
    df = pd.merge(df, df_rh, on='nome_link', how='left')

    # lógica da empresa para reclassificação: 
    # santa cruz: inicia com 000 ou está na faixa 0-99999999 -> lançado no 1000-padrao no coupa, precisa reclassificar para o cc correto no começo de cada mês
    # oncoprod: inicia com 200 -> -> lançado no 1000-padrao no coupa, precisa reclassificar para o cc correto no começo de cada mês
    # panpharma: inicia com 1000 -> não precisa reclassificar

    # função para verificar se o centro de custo é apto para reclassificação
    # função recebe o centro de custo, remove pontos e espaços, valida se tem mesmo um centro de custo, e depois aplica a lógica para determinar empresa e necessidade de reclassificação
    # retorna uma lista com o centro de custo para lançamento, a empresa e a observação de reclassificação

    #pd.series é usado para retornar várias colunas ao mesmo tempo
    
    def apto_reclassficao(cc):
        # split('.') tira .0 strip() e espaços
        cc_str = str(cc).split('.')[0].strip()
    
        if cc_str == 'nan' or cc_str == '':
            return pd.Series(["Pendente", "Não Identificado", "Verificar"])

        if cc_str.startswith('000') or (cc_str.isdigit() and int(cc_str) < 10000000):
            return pd.Series(["1000-PADRAO", "Santa Cruz", "Sim (Reclassificar)"])
        
        elif cc_str.startswith('200'):
            return pd.Series(["1000-PADRAO", "Oncoprod", "Sim (Reclassificar)"])
        
        elif cc_str.startswith('1000'):
            return pd.Series([cc_str, "Panpharma", "Não"])
        
        else:
            return pd.Series([cc_str, "Outra Empresa", "Verificar"])

    # lógica de reclassificação
    if 'centro_custo_final' in df.columns:
        df[['cc_lancamento', 'empresa', 'obs_reclass']] = df['centro_custo_final'].apply(apto_reclassficao)
    else:
        df['cc_lancamento'], df['empresa'], df['obs_reclass'] = "Pendente", "Não Identificada", "Verificar"

    # limpando o df pra ter só as colunas necessáarias

    minhas_colunas = ['cc_lancamento', 'empresa', 'obs_reclass']

    col_valor_original = [c for c in df.columns if 'valor' in c.lower()]
    colunas_da_fatura = [c for c in df_localiza.columns if c in df.columns]
    
    # junta as duas listas
    selecao_final = colunas_da_fatura + minhas_colunas
    
    # filtra apenas o que existe
    df_limpo = df[selecao_final].copy()

    if col_valor_original:
        cv = col_valor_original[0]
        df_limpo[cv] = df_limpo[cv].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_limpo[cv] = pd.to_numeric(df_limpo[cv], errors='coerce').fillna(0)

    return df_limpo