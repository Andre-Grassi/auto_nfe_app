# Script completo para build do app + instalador
# Executa tudo: venv, limpa build, instala deps, flet build, compila instalador

# Muda para o diretório raiz do projeto (pai da pasta installer)
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    # ============================================
    # ETAPA 1: Ativar ambiente virtual
    # ============================================
    $venvPath = ".\.venv\Scripts\Activate.ps1"
    if (Test-Path $venvPath) {
        Write-Host "`n[1/5] Ativando ambiente virtual..." -ForegroundColor Cyan
        & $venvPath
    } else {
        Write-Host "Erro: Ambiente virtual não encontrado em $venvPath" -ForegroundColor Red
        exit 1
    }

    # ============================================
    # ETAPA 2: Deletar pasta build
    # ============================================
    $buildPath = ".\build"
    if (Test-Path $buildPath) {
        Write-Host "`n[2/5] Deletando pasta build..." -ForegroundColor Yellow
        try {
            # Mata processos que podem estar travando arquivos
            Get-Process | Where-Object {$_.Path -like "*auto_nfe_app*"} | Stop-Process -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Remove-Item -Recurse -Force $buildPath -ErrorAction Stop
            Write-Host "Pasta build deletada com sucesso." -ForegroundColor Green
        } catch {
            Write-Host "Aviso: Não foi possível deletar completamente a pasta build. Continuando..." -ForegroundColor Yellow
            Write-Host $_.Exception.Message -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n[2/5] Pasta build não existe, pulando..." -ForegroundColor Gray
    }

    # ============================================
    # ETAPA 3: Instalar pacote auto_nfe
    # ============================================
    Write-Host "`n[3/5] Instalando pacote auto_nfe..." -ForegroundColor Cyan
    pip install ..\nfe_automatico\
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao instalar auto_nfe" -ForegroundColor Red
        exit 1
    }

    # ============================================
    # ETAPA 4: Build com Flet
    # ============================================
    Write-Host "`n[4/5] Executando flet build windows..." -ForegroundColor Cyan
    flet build windows --clear-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro no flet build" -ForegroundColor Red
        exit 1
    }
    Write-Host "Build do Flet concluído!" -ForegroundColor Green

    # ============================================
    # ETAPA 5: Compilar instalador
    # ============================================
    Write-Host "`n[5/5] Compilando instalador..." -ForegroundColor Cyan

    # Lê a versão do pyproject.toml
    $pyprojectPath = ".\pyproject.toml"
    $content = Get-Content $pyprojectPath -Raw

    if ($content -match 'version\s*=\s*"([^"]+)"') {
        $version = $Matches[1]
        Write-Host "Versão encontrada: $version" -ForegroundColor Green
    } else {
        Write-Host "Erro: Não foi possível encontrar a versão no pyproject.toml" -ForegroundColor Red
        exit 1
    }

    # Encontrar o compilador Inno Setup
    # Tenta: 1) comando iscc no PATH, 2) caminhos padrão, 3) mostra tutorial
    $isccCommand = $null
    
    # Tentativa 1: Verificar se iscc está no PATH
    $isccInPath = Get-Command "iscc" -ErrorAction SilentlyContinue
    if ($isccInPath) {
        $isccCommand = "iscc"
        Write-Host "Usando ISCC do PATH: $($isccInPath.Source)" -ForegroundColor Gray
    } else {
        # Tentativa 2: Verificar caminhos de instalação padrão
        $possiblePaths = @(
            "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            "C:\Program Files\Inno Setup 6\ISCC.exe",
            "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
        )
        
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                $isccCommand = $path
                Write-Host "Usando ISCC em: $path" -ForegroundColor Gray
                break
            }
        }
    }
    
    # Se não encontrou, mostrar tutorial
    if (-not $isccCommand) {
        Write-Host "`n========================================" -ForegroundColor Red
        Write-Host "ERRO: Inno Setup não encontrado!" -ForegroundColor Red
        Write-Host "========================================`n" -ForegroundColor Red
        
        Write-Host "Para instalar o Inno Setup:" -ForegroundColor Yellow
        Write-Host "  1. Baixe em: https://jrsoftware.org/isdl.php" -ForegroundColor White
        Write-Host "  2. Execute o instalador" -ForegroundColor White
        Write-Host ""
        Write-Host "Para adicionar ao PATH (recomendado):" -ForegroundColor Yellow
        Write-Host "  1. Pressione Win + R, digite 'sysdm.cpl' e pressione Enter" -ForegroundColor White
        Write-Host "  2. Va em 'Avancado' > 'Variaveis de Ambiente'" -ForegroundColor White
        Write-Host "  3. Em 'Variaveis do sistema', selecione 'Path' e clique 'Editar'" -ForegroundColor White
        Write-Host "  4. Clique 'Novo' e adicione:" -ForegroundColor White
        Write-Host "     C:\Program Files (x86)\Inno Setup 6" -ForegroundColor Cyan
        Write-Host "  5. Clique OK em todas as janelas" -ForegroundColor White
        Write-Host "  6. Reinicie o PowerShell" -ForegroundColor White
        Write-Host ""
        exit 1
    }

    # Compila o instalador passando a versão como parâmetro
    & $isccCommand /DMyAppVersion="$version" ".\installer\installer.iss"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "BUILD COMPLETO!" -ForegroundColor Green
        Write-Host "Instalador: installer\output\AutoNFe_Setup_$version.exe" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host "Erro ao compilar o instalador" -ForegroundColor Red
        exit 1
    }

} finally {
    # Retorna ao diretório original
    Pop-Location
}
