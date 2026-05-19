import pandas as pd
import glob
import os

def processar_resultados(diretorio_entrada, protocolo, skip_rows=5):
    arquivos = glob.glob(os.path.join(diretorio_entrada, "*.csv"))
    
    lista_tempo_resposta =[]
    lista_max_resposta = []
    lista_vazao =[]

    for arquivo in arquivos:
        # Carrega o CSV e garante que está ordenado pelo tempo de início
        df = pd.read_csv(arquivo).sort_values('timeStamp')
        
        # --- FILTRO DE WARM-UP ---
        if len(df) > skip_rows:
            df_estavel = df.iloc[skip_rows:].copy()
        else:
            print(f"Aviso: O arquivo {arquivo} tem poucas linhas. Pulando filtro.")
            df_estavel = df.copy()
        
        # 1. TEMPOS DE RESPOSTA (Latência)
        media_elapsed = df_estavel['elapsed'].mean()
        max_elapsed = df_estavel['elapsed'].max() # Pega o pico de latência deste teste específico
        
        lista_tempo_resposta.append(media_elapsed)
        lista_max_resposta.append(max_elapsed)
        
        # 2. VAZÃO (Throughput)
        tempo_inicio_ms = df_estavel['timeStamp'].min()
        tempo_fim_ms = (df_estavel['timeStamp'] + df_estavel['elapsed']).max()
        
        tempo_total_ms = tempo_fim_ms - tempo_inicio_ms
        total_requisicoes = len(df_estavel)
        
        vazao = total_requisicoes / (tempo_total_ms / 1000) if tempo_total_ms > 0 else 0
        lista_vazao.append(vazao)

    # Cria o DataFrame base com as 30 execuções
    resumo = pd.DataFrame({
        'execucao':[f"Teste_{i+1}" for i in range(len(lista_tempo_resposta))],
        'media_tempo_resposta_ms': lista_tempo_resposta,
        'max_tempo_resposta_ms': lista_max_resposta,
        'throughput_req_sec': lista_vazao
    })

    # CÁLCULO DAS ESTATÍSTICAS GLOBAIS
    stats_globais = pd.DataFrame([
        {
            'execucao': 'MEDIA_GLOBAL',
            'media_tempo_resposta_ms': resumo['media_tempo_resposta_ms'].mean(),
            'max_tempo_resposta_ms': resumo['max_tempo_resposta_ms'].mean(),
            'throughput_req_sec': resumo['throughput_req_sec'].mean()
        },
        {
            'execucao': 'DESVIO_PADRAO',
            'media_tempo_resposta_ms': resumo['media_tempo_resposta_ms'].std(),
            'max_tempo_resposta_ms': resumo['max_tempo_resposta_ms'].std(),
            'throughput_req_sec': resumo['throughput_req_sec'].std()
        },
        {
            'execucao': 'PICO_MAXIMO_GLOBAL',
            'media_tempo_resposta_ms': resumo['media_tempo_resposta_ms'].max(), # A maior média registrada
            'max_tempo_resposta_ms': resumo['max_tempo_resposta_ms'].max(),     # A latência mais alta de TODA a bateria
            'throughput_req_sec': resumo['throughput_req_sec'].max()            # A maior vazão atingida
        }
    ])

    resumo_final = pd.concat([resumo, stats_globais], ignore_index=True)
    print(f"\n--- Processamento concluído ({protocolo}) - Ignoradas {skip_rows} iniciais ---")
    return resumo_final

# =====================================================================
# --- CONFIGURAÇÕES DE PASTAS ---
# =====================================================================

# 1. Pastas onde os testes originais do JMeter (.csv) estão salvos
DIR_ENTRADA_REST = "D:/Teste_REST/vazao_latencia/update"
DIR_ENTRADA_GRPC = "D:/Teste_gRPC/vazao_latencia/update"

# 2. Pastas onde você quer salvar o relatório final (Pode mudar para onde preferir)
DIR_SAIDA_REST = "D:/Teste_REST/vazao_latencia/update/Resultado"
DIR_SAIDA_GRPC = "D:/Teste_gRPC/vazao_latencia/update/Resultado"

# Garante que as pastas de saída existem (se não existirem, o Python cria)
os.makedirs(DIR_SAIDA_REST, exist_ok=True)
os.makedirs(DIR_SAIDA_GRPC, exist_ok=True)

# --- EXECUÇÃO ---
# Processa os dados
df_rest = processar_resultados(DIR_ENTRADA_REST, "REST")
df_grpc = processar_resultados(DIR_ENTRADA_GRPC, "gRPC")

# Monta o caminho final dos arquivos
arquivo_rest = os.path.join(DIR_SAIDA_REST, "resumo_rest.csv")
arquivo_grpc = os.path.join(DIR_SAIDA_GRPC, "resumo_grpc.csv")

# Salva em CSV
df_rest.to_csv(arquivo_rest, index=False)
df_grpc.to_csv(arquivo_grpc, index=False)

print(f"\n✅ Relatório REST salvo com sucesso em:\n -> {arquivo_rest}")
print(f"✅ Relatório gRPC salvo com sucesso em:\n -> {arquivo_grpc}")