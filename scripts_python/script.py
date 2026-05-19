import pandas as pd
import requests
import os

# --- CONFIGURAÇÕES ---
PROMETHEUS_URL = "http://localhost:9090"
CPU_METRIC = 'process_cpu_usage' 
MEM_METRIC = 'jvm_memory_used_bytes{area="heap"}'

DIR_JMETER = "D:/Teste_gRPC/CPU/update"
DIR_SAIDA = "D:/Teste_gRPC/CPU/update/Update_Telemetria"

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
                df['timestamp'] = pd.to_numeric(df['timestamp'])
                return df
    except Exception as e:
        print(f"Erro: {e}")
    return None

# --- LOOP PRINCIPAL ---
arquivos = [f for f in os.listdir(DIR_JMETER) if f.endswith(".csv")]

for arquivo in arquivos:
    print(f"Processando: {arquivo}")
    path_csv = os.path.join(DIR_JMETER, arquivo)
    
    # 1. Ler CSV do JMeter
    df_j = pd.read_csv(path_csv)
    if df_j.empty: continue

    t_inicio_teste_ms = df_j['timeStamp'].min()
    t_fim_teste_ms = (df_j['timeStamp'] + df_j['elapsed']).max()
    
    start_sec = (t_inicio_teste_ms / 1000) - 30
    
    end_sec = (t_fim_teste_ms / 1000) + 60
    
    # 2. Busca Dados
    df_cpu = consultar_prometheus(start_sec, end_sec, CPU_METRIC)
    df_mem = consultar_prometheus(start_sec, end_sec, MEM_METRIC)
    
    # 3. Salva
    if df_cpu is not None and df_mem is not None:
        df_cpu.rename(columns={'valor': 'cpu_usage'}, inplace=True)
        df_mem.rename(columns={'valor': 'mem_bytes'}, inplace=True)
        
        df_final = pd.merge(df_cpu, df_mem, on='timestamp', how='outer').sort_values('timestamp')
        
        t_inicio_sec = t_inicio_teste_ms / 1000
        t_fim_sec = t_fim_teste_ms / 1000
        
        def definir_fase(row):
            ts = row['timestamp']
            if ts < t_inicio_sec: return 'Baseline'
            elif ts > t_fim_sec: return 'Cooldown'
            else: return 'Teste'
            
        df_final['fase'] = df_final.apply(definir_fase, axis=1)

        df_final.to_csv(os.path.join(DIR_SAIDA, arquivo.replace(".csv", "_telemetria.csv")), index=False)
        print(" -> OK")
    else:
        print(" -> Falha na coleta (Dados nulos)")