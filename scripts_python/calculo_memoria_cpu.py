import pandas as pd
import glob
import os

def processar_telemetria(diretorio_entrada, protocolo):
    arquivos = glob.glob(os.path.join(diretorio_entrada, "*.csv"))
    
    lista_media_cpu = []
    lista_max_cpu = []
    lista_max_memoria_mb =[]

    for arquivo in arquivos:
        # Carrega o CSV de telemetria
        df = pd.read_csv(arquivo).sort_values('timestamp')
        
        # --- A CORREÇÃO DE OURO ---
        # Filtra os dados APENAS para o momento em que o JMeter estava rodando
        # Se você não filtrar, os zeros do Baseline e Cooldown vão destruir sua média!
        df_teste = df[df['fase'] == 'Teste']
        
        # 1. CPU (Calculada APENAS durante a fase 'Teste')
        # Usamos o df_teste para ter a média real do estresse
        if not df_teste.empty:
            media_cpu = df_teste['cpu_usage'].mean()
            max_cpu = df_teste['cpu_usage'].max()
        else:
            media_cpu = 0
            max_cpu = 0
        
        # 2. MEMÓRIA (Pico Heap Total)
        # O max() pode ser tirado do arquivo inteiro (df), pois o pico absoluto
        # é o que importa para a infraestrutura, não importa a fase exata.
        max_memoria_bytes = df['mem_bytes'].max()
        max_memoria_mb = max_memoria_bytes / (1024 * 1024)
        
        lista_media_cpu.append(media_cpu)
        lista_max_cpu.append(max_cpu)
        lista_max_memoria_mb.append(max_memoria_mb)

    # Cria o DataFrame base com as 30 execuções
    resumo = pd.DataFrame({
        'execucao':[f"Teste_{i+1}" for i in range(len(lista_media_cpu))],
        'media_cpu': lista_media_cpu,
        'max_cpu': lista_max_cpu,
        'max_memoria_mb': lista_max_memoria_mb
    })

    # CÁLCULO DAS ESTATÍSTICAS GLOBAIS
    stats_globais = pd.DataFrame([
        {
            'execucao': 'MEDIA_GLOBAL',
            'media_cpu': resumo['media_cpu'].mean(),
            'max_cpu': resumo['max_cpu'].mean(),
            'max_memoria_mb': resumo['max_memoria_mb'].mean() 
        },
        {
            'execucao': 'DESVIO_PADRAO',
            'media_cpu': resumo['media_cpu'].std(),
            'max_cpu': resumo['max_cpu'].std(),
            'max_memoria_mb': resumo['max_memoria_mb'].std()
        },
        {
            'execucao': 'PICO_MAXIMO_GLOBAL',
            'media_cpu': resumo['media_cpu'].max(),
            'max_cpu': resumo['max_cpu'].max(),
            'max_memoria_mb': resumo['max_memoria_mb'].max() 
        }
    ])

    resumo_final = pd.concat([resumo, stats_globais], ignore_index=True)
    print(f"\n--- Processamento de Telemetria concluído ({protocolo}) ---")
    return resumo_final

# =====================================================================
# --- CONFIGURAÇÕES DE PASTAS ---
# =====================================================================

DIR_ENTRADA_REST = "D:/Teste_REST/CPU_memoria/update/Update_Telemetria"
DIR_ENTRADA_GRPC = "D:/Teste_gRPC/CPU_memoria/update/Update_Telemetria"

DIR_SAIDA_REST = "D:/Teste_REST/CPU_memoria/update/Resultado"
DIR_SAIDA_GRPC = "D:/Teste_gRPC/CPU_memoria/update/Resultado"

os.makedirs(DIR_SAIDA_REST, exist_ok=True)
os.makedirs(DIR_SAIDA_GRPC, exist_ok=True)

# --- EXECUÇÃO ---
df_rest = processar_telemetria(DIR_ENTRADA_REST, "REST")
df_grpc = processar_telemetria(DIR_ENTRADA_GRPC, "gRPC")

arquivo_rest = os.path.join(DIR_SAIDA_REST, "resumo_rest.csv")
arquivo_grpc = os.path.join(DIR_SAIDA_GRPC, "resumo_grpc.csv")

df_rest.to_csv(arquivo_rest, index=False)
df_grpc.to_csv(arquivo_grpc, index=False)

print(f"\n✅ Relatório de Telemetria REST salvo com sucesso em:\n -> {arquivo_rest}")
print(f"✅ Relatório de Telemetria gRPC salvo com sucesso em:\n -> {arquivo_grpc}")