import pandas as pd
import scipy.stats as stats
import os

def executar_analise_estatistica(arquivo_rest, arquivo_grpc, metrica, nome_metrica, operacao, alpha=0.05):
    # 1. Carrega os dados
    df_rest = pd.read_csv(arquivo_rest)
    df_grpc = pd.read_csv(arquivo_grpc)

    # 2. Filtra apenas as linhas de execução reais (ignora MEDIA_GLOBAL, etc.)
    dados_rest = df_rest[df_rest['execucao'].str.startswith('Teste_')][metrica].astype(float)
    dados_grpc = df_grpc[df_grpc['execucao'].str.startswith('Teste_')][metrica].astype(float)

    print(f"\n{'='*75}")
    print(f" 🔬 RELATÓRIO ESTATÍSTICO: {nome_metrica.upper()} | OPERAÇÃO: {operacao.upper()}")
    print(f"{'='*75}")
    print(f"Tamanho da amostra REST: {len(dados_rest)} | gRPC: {len(dados_grpc)}\n")

    # ==========================================
    # PASSO 1: TESTE DE NORMALIDADE (SHAPIRO-WILK)
    # ==========================================
    stat_sw_rest, p_sw_rest = stats.shapiro(dados_rest)
    stat_sw_grpc, p_sw_grpc = stats.shapiro(dados_grpc)

    rest_normal = p_sw_rest > alpha
    grpc_normal = p_sw_grpc > alpha

    # ==========================================
    # PASSO 2: ESCOLHA DO TESTE DE HIPÓTESE
    # ==========================================
    if rest_normal and grpc_normal:
        nome_teste = "Teste T de Welch"
        motivo_escolha = "✅ Ambas as amostras (REST e gRPC) apresentaram distribuição NORMAL."
        stat_hip, p_hip = stats.ttest_ind(dados_rest, dados_grpc, equal_var=False)
    else:
        nome_teste = "Teste de Mann-Whitney U"
        
        # Identifica exatamente quem causou a escolha do teste não-paramétrico
        if not rest_normal and not grpc_normal:
            motivo_escolha = "⚠️ NENHUMA das amostras (REST e gRPC) apresentou distribuição normal."
        elif not rest_normal:
            motivo_escolha = "⚠️ A amostra do REST NÃO apresentou distribuição normal (gRPC foi normal)."
        else:
            motivo_escolha = "⚠️ A amostra do gRPC NÃO apresentou distribuição normal (REST foi normal)."
            
        stat_hip, p_hip = stats.mannwhitneyu(dados_rest, dados_grpc, alternative='two-sided')

    print(f"📌 JUSTIFICATIVA ESTATÍSTICA:")
    print(f"   {motivo_escolha}")
    print(f"   -> Aplicando o {nome_teste}...\n")

    # ==========================================
    # PASSO 3: CONCLUSÃO FINAL
    # ==========================================
    media_rest = dados_rest.mean()
    mediana_rest = dados_rest.median()
    media_grpc = dados_grpc.mean()
    mediana_grpc = dados_grpc.median()
    
    if p_hip < alpha:
        print(f"🔴 VEREDITO: HÁ DIFERENÇA estatisticamente significativa entre REST e gRPC.")
        print(f"   (P-Valor final do teste: {p_hip:.5e})")
    else:
        print(f"🟢 VEREDITO: NÃO HÁ diferença significativa. O resultado é um EMPATE TÉCNICO.")
        print(f"   (P-Valor final do teste: {p_hip:.5e})")
        
    print(f"\n📊 Resumo dos Dados:")
    
    # Se a métrica for CPU, multiplica por 100 para mostrar em Porcentagem no relatório
    if metrica == 'media_cpu' or metrica == 'max_cpu':
        print(f"   [REST] Média: {(media_rest*100):.4f}% | Mediana: {(mediana_rest*100):.4f}%")
        print(f"[gRPC] Média: {(media_grpc*100):.4f}% | Mediana: {(mediana_grpc*100):.4f}%")
    else:
        print(f"[REST] Média: {media_rest:.4f} | Mediana: {mediana_rest:.4f}")
        print(f"   [gRPC] Média: {media_grpc:.4f} | Mediana: {mediana_grpc:.4f}")
        
    print(f"{'='*75}\n")


# =====================================================================
# --- AUTOMATIZAÇÃO DE TODAS AS OPERAÇÕES ---
# =====================================================================

operacoes =['create', 'read', 'update', 'delete']

for op in operacoes:
    print(f"\n\n\n" + "#"*80)
    print(f"🚀 INICIANDO ANÁLISE DA OPERAÇÃO: {op.upper()}")
    print("#"*80)
    
    arquivo_vazao_rest = f"D:/Teste_REST/vazao_latencia/{op}/Resultado/resumo_rest.csv"
    arquivo_vazao_grpc = f"D:/Teste_gRPC/vazao_latencia/{op}/Resultado/resumo_grpc.csv"

    arquivo_cpu_rest = f"D:/Teste_REST/CPU_memoria/{op}/Resultado/resumo_rest.csv"
    arquivo_cpu_grpc = f"D:/Teste_gRPC/CPU_memoria/{op}/Resultado/resumo_grpc.csv"
    
    # 1. Teste para Latência Média
    try:
        executar_analise_estatistica(arquivo_vazao_rest, arquivo_vazao_grpc, 'media_tempo_resposta_ms', 'Latência Média (ms)', op)
    except FileNotFoundError:
        print(f"⚠️ Aviso: Arquivos de Vazão/Latência não encontrados para a operação '{op}'.")

    # 2. Teste para Vazão
    try:
        executar_analise_estatistica(arquivo_vazao_rest, arquivo_vazao_grpc, 'throughput_req_sec', 'Vazão (Req/Sec)', op)
    except FileNotFoundError:
        pass 

    # 3. Teste para CPU (Uso Médio)
    try:
        executar_analise_estatistica(arquivo_cpu_rest, arquivo_cpu_grpc, 'media_cpu', 'Uso de CPU Médio (%)', op)
    except FileNotFoundError:
        print(f"⚠️ Aviso: Arquivos de CPU/Memória não encontrados para a operação '{op}'.")

    # 4. Teste para Pico de Memória (Heap Total)
    try:
        executar_analise_estatistica(arquivo_cpu_rest, arquivo_cpu_grpc, 'max_memoria_mb', 'Pico de Memória Heap (MB)', op)
    except FileNotFoundError:
        pass