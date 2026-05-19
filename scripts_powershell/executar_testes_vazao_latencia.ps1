# =======================================================================
# SCRIPT MAESTRO - VAZÃO E LATÊNCIA
# =======================================================================

$jarPath      = "D:\JavaProjects\projeto-tcc-rest\api-rest\target\api-rest-0.0.1-SNAPSHOT.jar"
$jmeterPath   = "D:\apache-jmeter-5.6.3\bin\jmeter.bat"
$jmxPath      = "D:\api_rest_create.jmx"
$outputFolder = "D:\Teste_REST\vazao_latencia\create"
$apiPort      = 8080

# --- 1. LOCALIZAR JAVA AUTOMATICAMENTE ---
Write-Host "Verificando instalação do Java..." -ForegroundColor DarkGray
try {
    $javaExe = (Get-Command "java" -ErrorAction Stop).Source
    Write-Host "Java encontrado em: $javaExe" -ForegroundColor Green
} catch {
    Write-Host "ERRO CRÍTICO: O comando 'java' não foi encontrado." -ForegroundColor Red
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
for ($i = 1; $i -le 30; $i++) {
    Write-Host "`n------------------------------------------------" -ForegroundColor Cyan
    Write-Host "Iniciando Ciclo $i de 30 (Vazão e Latência)..." -ForegroundColor Cyan

    # Arquivos de log separados (A novidade que você pediu)
    $logOut = "$outputFolder\api_log_out_$i.txt"
    $logErr = "$outputFolder\api_log_err_$i.txt"

    # A) Inicia a API gerando os logs e ocultando a janela
    try {
        $appProcess = Start-Process -FilePath $javaExe -ArgumentList "-Xms512m", "-Xmx512m", "-jar", "$jarPath" -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru -NoNewWindow
    } catch {
        Write-Host "ERRO AO INICIAR PROCESSO JAVA" -ForegroundColor Red
        Break
    }
    
    # B) Aguarda a porta abrir
    Write-Host "Aguardando API na porta $apiPort..." -NoNewline
    $attempts = 0
    $apiReady = $false

    while ($attempts -lt 60) {
        if (Test-PortaSilenciosa -porta $apiPort) {
            $apiReady = $true
            break
        }
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
        $attempts++
    }

    if (-not $apiReady) {
        Write-Host "`nERRO: API não subiu após 60s. Verifique os logs: $logErr" -ForegroundColor Red
        Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force
        continue 
    }
    Write-Host " OK!" -ForegroundColor Green

    # Dá apenas 2 segundinhos para o Spring Boot "respirar" antes do ataque
    Start-Sleep -Seconds 2

    # C) Roda o JMeter
    $resultFile = "$outputFolder\resultado_$i.csv"
    Write-Host "Rodando teste de carga JMeter (Cold Start)..." -ForegroundColor Yellow
    
    $argList = @("-n", "-t", "$jmxPath", "-l", "$resultFile")
    Start-Process -FilePath $jmeterPath -ArgumentList $argList -Wait -NoNewWindow

    # D) Encerra a API
    Write-Host "Teste finalizado. Encerrando API e limpando ambiente..."
    Stop-Process -Id $appProcess.Id -Force -ErrorAction SilentlyContinue
    Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force
    
    # E) Garante a liberação da porta antes do próximo ciclo
    Write-Host "Aguardando liberação da porta $apiPort..." -NoNewline
    while (Test-PortaSilenciosa -porta $apiPort) {
        Start-Sleep -Seconds 1
        Write-Host "x" -NoNewline
    }
    Write-Host " Liberada!" -ForegroundColor Green
    
    Start-Sleep -Seconds 3
}

Write-Host "`nFim da bateria de testes de Vazão e Latência." -ForegroundColor Green