import pandas as pd
import requests
import os

# --- CONFIGURAÇÕES ---
PROMETHEUS_URL = "http://localhost:9090"
MEM_METRIC = 'jvm_memory_used_bytes{area="heap", id="G1 Old Gen"}'

DIR_JMETER = "D:/Teste_gRPC/Memoria/update"
DIR_SAIDA  = "D:/Teste_gRPC/Memoria/update/Resumo_Telemetria"

if not os.path.exists(DIR_SAIDA):
    os.makedirs(DIR_SAIDA)

def consultar_prometheus(start_ts, end_ts, query_str):
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params={
            'query': query_str,
            'start': start_ts,
            'end': end_ts,
            'step': '1s'
        })
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success' and len(data['data']['result']) > 0:
                values = data['data']['result'][0]['values']
                df = pd.DataFrame(values, columns=['timestamp', 'valor'])
                df['valor'] = pd.to_numeric(df['valor'])
                return df
    except Exception as e:
        print(f"Erro na consulta: {e}")
    return None

# Lista para guardar o resultado de cada um dos 30 testes
resultados_consolidados =[]

arquivos = [f for f in os.listdir(DIR_JMETER) if f.endswith(".csv")]
print(f"Iniciando extração do PLATÔ MÁXIMO de Memória (Old Gen) para {len(arquivos)} testes...\n")

for arquivo in arquivos:
    path_csv = os.path.join(DIR_JMETER, arquivo)
    
    df_j = pd.read_csv(path_csv)
    if df_j.empty: continue

    t_inicio_teste_ms = df_j['timeStamp'].min()
    t_fim_teste_ms = (df_j['timeStamp'] + df_j['elapsed']).max()
    
    start_sec = (t_inicio_teste_ms / 1000) - 30
    end_sec = (t_fim_teste_ms / 1000) + 60
    
    # Consulta o Prometheus
    df_mem = consultar_prometheus(start_sec, end_sec, MEM_METRIC)
    
    if df_mem is not None and not df_mem.empty:
       
        max_bytes = df_mem['valor'].max()
        
        # Converte para MB
        max_mb = max_bytes / (1024 * 1024)
        
        # Salva na lista de resultados
        resultados_consolidados.append({
            'arquivo_teste': arquivo,
            'max_old_gen_bytes': max_bytes,
            'max_old_gen_mb': round(max_mb, 2)
        })
        print(f" -> {arquivo}: Platô de {max_mb:.2f} MB")
    else:
        print(f" -> {arquivo}: FALHA (Sem dados no Prometheus)")

# --- GERAÇÃO DO ARQUIVO ÚNICO DE RESUMO ---
if resultados_consolidados:
    df_resumo = pd.DataFrame(resultados_consolidados)
    
    # Ordena pelo nome do arquivo (ex: teste_1, teste_2...)
    df_resumo.sort_values('arquivo_teste', inplace=True)
    
    caminho_resumo = os.path.join(DIR_SAIDA, "resumo_maximos_old_gen.csv")
    df_resumo.to_csv(caminho_resumo, index=False)
    
    print(f"\n✅ SUCESSO! Relatório consolidado gerado em:\n{caminho_resumo}")
else:
    print("\n❌ Nenhum dado foi processado.")