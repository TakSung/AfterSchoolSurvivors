# Windows 11 개발 환경 자동 설치 스크립트
# Python 3.13, VSCode, GitHub CLI, Windows Terminal, NVM 설치

# ===== 시작 메시지 =====
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "개발 환경 자동 설치 시작" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ===== ExecutionPolicy 설정 =====
Write-Host "[0/5] ExecutionPolicy 설정 중..." -ForegroundColor Yellow
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ ExecutionPolicy 설정 완료 (Python venv 활성화 가능)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ ExecutionPolicy 설정 실패 (수동 설정 필요)" -ForegroundColor Yellow
}
Write-Host ""

# ===== 관리자 권한 확인 =====
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ 이 스크립트는 관리자 권한이 필요합니다." -ForegroundColor Red
    Write-Host "PowerShell을 관리자 권한으로 실행한 후 다시 시도해주세요." -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "✅ 관리자 권한 확인 완료" -ForegroundColor Green
Write-Host ""

# ===== Step 1: Chocolatey 설치 확인 =====
Write-Host "[1/6] Chocolatey 설치 확인 중..." -ForegroundColor Yellow

if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "✅ Chocolatey가 이미 설치되어 있습니다." -ForegroundColor Green
} else {
    Write-Host "📦 Chocolatey 설치 중..." -ForegroundColor Cyan
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    # 환경 변수 새로고침
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine) + ";" + [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)

    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Host "✅ Chocolatey 설치 완료" -ForegroundColor Green
    } else {
        Write-Host "❌ Chocolatey 설치 실패" -ForegroundColor Red
        pause
        exit 1
    }
}
Write-Host ""

# ===== Step 2: 설치할 패키지 확인 =====
Write-Host "[2/6] 설치할 패키지 확인 중..." -ForegroundColor Yellow

$packagesToInstall = @{
    "python313" = "Python 3.13"
    "vscode" = "Visual Studio Code"
    "github-cli" = "GitHub CLI"
    "microsoft-windows-terminal" = "Windows Terminal"
    "nvm" = "NVM (Node Version Manager)"
}

$toInstall = @()
$alreadyInstalled = @()

foreach ($package in $packagesToInstall.Keys) {
    $packageName = $packagesToInstall[$package]
    $chocoList = choco list --local-only $package --exact

    if ($chocoList -match $package) {
        Write-Host "  ✓ $packageName 이미 설치됨 (건너뜀)" -ForegroundColor Gray
        $alreadyInstalled += $packageName
    } else {
        Write-Host "  + $packageName 설치 예정" -ForegroundColor Cyan
        $toInstall += $package
    }
}
Write-Host ""

# ===== Step 3: 필요한 패키지 설치 =====
if ($toInstall.Count -eq 0) {
    Write-Host "[3/6] 모든 패키지가 이미 설치되어 있습니다." -ForegroundColor Green
} else {
    Write-Host "[3/6] 개발 도구 설치 중... ($($toInstall.Count)개)" -ForegroundColor Yellow
    Write-Host "설치 항목: $($toInstall -join ', ')" -ForegroundColor Cyan
    Write-Host ""
    choco install $toInstall -y
}
Write-Host ""

# ===== Step 4: 설치 확인 =====
Write-Host "[4/6] 설치 확인 중..." -ForegroundColor Yellow

# 환경 변수 새로고침
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine) + ";" + [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)

$installStatus = @{
    "Python" = $false
    "VSCode" = $false
    "GitHub CLI" = $false
    "Windows Terminal" = $false
    "NVM" = $false
}

# Python 확인
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✅ Python 설치 완료: $pythonVersion" -ForegroundColor Green
    $installStatus["Python"] = $true
} else {
    Write-Host "❌ Python 설치 확인 실패" -ForegroundColor Red
}

# VSCode 확인
if (Get-Command code -ErrorAction SilentlyContinue) {
    $vscodeVersion = code --version | Select-Object -First 1
    Write-Host "✅ VSCode 설치 완료: $vscodeVersion" -ForegroundColor Green
    $installStatus["VSCode"] = $true
} else {
    Write-Host "❌ VSCode 설치 확인 실패" -ForegroundColor Red
}

# GitHub CLI 확인
if (Get-Command gh -ErrorAction SilentlyContinue) {
    $ghVersion = gh --version | Select-Object -First 1
    Write-Host "✅ GitHub CLI 설치 완료: $ghVersion" -ForegroundColor Green
    $installStatus["GitHub CLI"] = $true
} else {
    Write-Host "❌ GitHub CLI 설치 확인 실패" -ForegroundColor Red
}

# Windows Terminal 확인
if (Get-Command wt -ErrorAction SilentlyContinue) {
    Write-Host "✅ Windows Terminal 설치 완료" -ForegroundColor Green
    $installStatus["Windows Terminal"] = $true
} else {
    Write-Host "❌ Windows Terminal 설치 확인 실패 (재부팅 후 사용 가능)" -ForegroundColor Yellow
    $installStatus["Windows Terminal"] = $true
}

# NVM 확인
if (Get-Command nvm -ErrorAction SilentlyContinue) {
    $nvmVersion = nvm version
    Write-Host "✅ NVM 설치 완료: $nvmVersion" -ForegroundColor Green
    $installStatus["NVM"] = $true
} else {
    Write-Host "❌ NVM 설치 확인 실패 (터미널 재시작 후 사용 가능)" -ForegroundColor Yellow
    $installStatus["NVM"] = $true
}
Write-Host ""

# ===== Step 5: pip 업그레이드 =====
Write-Host "[5/6] pip 업그레이드 중..." -ForegroundColor Yellow
if ($installStatus["Python"]) {
    python -m pip install --upgrade pip
    Write-Host "✅ pip 업그레이드 완료" -ForegroundColor Green
} else {
    Write-Host "⚠️ Python이 설치되지 않아 pip 업그레이드를 건너뜁니다." -ForegroundColor Yellow
}
Write-Host ""

# ===== Step 6: Python venv 테스트 =====
Write-Host "[6/6] Python 가상환경 테스트 중..." -ForegroundColor Yellow
if ($installStatus["Python"]) {
    try {
        $testVenvPath = Join-Path $env:TEMP "test_venv"
        if (Test-Path $testVenvPath) {
            Remove-Item -Recurse -Force $testVenvPath
        }

        python -m venv $testVenvPath
        $activateScript = Join-Path $testVenvPath "Scripts\Activate.ps1"

        if (Test-Path $activateScript) {
            Write-Host "✅ Python venv 생성 및 활성화 가능 (ExecutionPolicy 정상)" -ForegroundColor Green
            Remove-Item -Recurse -Force $testVenvPath
        } else {
            Write-Host "⚠️ venv 생성됨, 하지만 활성화 스크립트를 찾을 수 없음" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ venv 테스트 실패: $_" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️ Python이 설치되지 않아 venv 테스트를 건너뜁니다." -ForegroundColor Yellow
}
Write-Host ""

# ===== Step 7: 설치 결과 요약 =====
Write-Host "[7/7] 설치 결과 요약" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

if ($alreadyInstalled.Count -gt 0) {
    Write-Host ""
    Write-Host "이미 설치되어 있던 항목:" -ForegroundColor Gray
    foreach ($item in $alreadyInstalled) {
        Write-Host "  ○ $item" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "설치 확인 결과:" -ForegroundColor White

$allSuccess = $true
foreach ($tool in $installStatus.Keys) {
    if ($installStatus[$tool]) {
        Write-Host "✅ $tool" -ForegroundColor Green
    } else {
        Write-Host "❌ $tool" -ForegroundColor Red
        $allSuccess = $false
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allSuccess) {
    Write-Host "🎉 모든 도구 설치 완료!" -ForegroundColor Green
} else {
    Write-Host "⚠️ 일부 도구 설치에 실패했습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
