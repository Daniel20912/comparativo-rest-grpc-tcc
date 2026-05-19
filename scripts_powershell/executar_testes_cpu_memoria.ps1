# =======================================================================
# SCRIPT MAESTRO - CPU E MEMÓRIA
# =======================================================================

# --- CONFIGURAÇÕES ---
$jarPath      = "D:\JavaProjects\projeto-tcc-grpc\api-grpc\target\api-grpc-0.0.1-SNAPSHOT.jar"
$jmeterPath   = "D:\apache-jmeter-5.6.3\bin\jmeter.bat"
$jmxPath      = "D:\api_grpc_update_cpu.jmx"
$outputFolder = "D:\Teste_gRPC\CPU\update"
$apiPort      = 9091

# --- TEMPOS (METODOLOGIA) ---
$totalBaterias    = 30
$jmeterStartDelay = 60 # Tempo para Baseline
$tempoCooldown    = 60 # Tempo pós-teste

# --- 1. LOCALIZAR JAVA AUTOMATICAMENTE ---
Write-Host "Verificando instalação do Java..." -ForegroundColor DarkGray
try {
    $javaExe = (Get-Command "java" -ErrorAction Stop).Source
    Write-Host "Java encontrado em: $javaExe" -ForegroundColor Green
} catch {
    Write-Host "ERRO CRÍTICO: O comando 'java' não foi encontrado no sistema." -ForegroundColor Red
    Break
}

# --- 2. PREPARAÇÃO ---
if (!(Test-Path $outputFolder)) { New-Item -ItemType Directory -Path $outputFolder -Force | Out-Null }

Write-Host "Limpando processos Java antigos..." -ForegroundColor DarkGray
Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force

function Test-PortaSilenciosa ($porta) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $connect = $tcp.BeginConnect("localhost", $porta, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne(500, $false)
        if ($tcp.Connected) { $tcp.Close(); return $true }
        return $wait -and $tcp.Client.Connected
    } catch {
        return $false
    }
}

# --- 3. LOOP PRINCIPAL ---
for ($i = 1; $i -le $totalBaterias; $i++) {
    Write-Host "`n------------------------------------------------" 
    Write-Host "EXECUCAO $i de $totalBaterias" -ForegroundColor Cyan
    
    $logOut = "$outputFolder\api_log_out_$i.txt"
    $logErr = "$outputFolder\api_log_err_$i.txt"

    # A) Inicia API
    try {
        $apiProcess = Start-Process -FilePath $javaExe -ArgumentList "-Xms512m", "-Xmx512m", "-jar", "$jarPath" -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru -NoNewWindow
    } catch {
        Write-Host "ERRO AO INICIAR PROCESSO JAVA:" -ForegroundColor Red
        Break
    }
    
    # B) Aguarda Porta
    Write-Host "Aguardando API na porta $apiPort..." -NoNewline
    $attempts = 0
    $isReady = $false
    
    while ($attempts -lt 60) {
        if (Test-PortaSilenciosa -porta $apiPort) {
            $isReady = $true
            break
        }
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
        $attempts++
    }
    
    if (-not $isReady) {
        Write-Host "`nERRO FATAL: API não subiu após 60s." -ForegroundColor Red
        Write-Host "Verifique os erros no arquivo: $logErr" -ForegroundColor Yellow
        Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force
        continue
    }
    Write-Host " OK!" -ForegroundColor Green

    Start-Sleep -Seconds 5

    # C) Dispara JMeter
    $resultFile = "$outputFolder\resultado_$i.csv"
    Write-Host "Iniciando JMeter (Delay: ${jmeterStartDelay}s)..." -ForegroundColor Yellow
    
    $jmeterArgs = @("-n", "-t", "$jmxPath", "-l", "$resultFile", "-Jdelay=$jmeterStartDelay")

    Start-Process -FilePath $jmeterPath -ArgumentList $jmeterArgs -Wait -NoNewWindow
    Write-Host "Teste JMeter finalizado." -ForegroundColor Green
    
    # D) Cooldown
    Write-Host "Aguardando Cooldown ($tempoCooldown s)..."
    Start-Sleep -Seconds $tempoCooldown
    
    # E) ENCERRA API
    Write-Host "Encerrando API e limpando ambiente..."
    Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
    
    # Garante que nenhum Java sobreviva (Opção Nuclear)
    Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force
    
    # Checa se o Windows realmente soltou a porta antes de iniciar o próximo ciclo
    Write-Host "Aguardando liberação da porta $apiPort..." -NoNewline
    while (Test-PortaSilenciosa -porta $apiPort) {
        Start-Sleep -Seconds 1
        Write-Host "x" -NoNewline
    }
    Write-Host " Liberada!" -ForegroundColor Green
    
    Start-Sleep -Seconds 3
}
Write-Host "`nFim da bateria de testes." -ForegroundColor Green