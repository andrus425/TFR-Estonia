param(
    [ValidateRange(30,600)][int]$Seconds = 120,
    [switch]$ParentOnly,
    [switch]$ArithmeticQA,
    [string]$GameDirectory = 'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
)
$ErrorActionPreference = 'Stop'
$modWorkspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$profileDirectory = [IO.Path]::GetFullPath((Join-Path $modWorkspace '..\..'))
if ((Split-Path $profileDirectory -Leaf) -ne 'Hearts of Iron IV') {
    throw 'The mod must be installed under the Hearts of Iron IV user-profile mod directory.'
}
$executablePath = Join-Path $GameDirectory 'hoi4.exe'
if (-not (Test-Path -LiteralPath $executablePath)) { throw "Missing game executable: $executablePath" }
if (Get-Process -Name hoi4 -ErrorAction SilentlyContinue) { throw 'An existing HOI4 session is running. Close it before using the smoke test.' }
$loadFile = Join-Path $profileDirectory 'dlc_load.json'
$hadLoadFile = Test-Path -LiteralPath $loadFile
$previousBytes = if ($hadLoadFile) { [IO.File]::ReadAllBytes($loadFile) } else { $null }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$kind = if ($ParentOnly) { 'parent' } elseif ($ArithmeticQA) { 'estonia-qa' } else { 'estonia' }
$outputDirectory = Join-Path $modWorkspace "test-output\engine-$kind-$stamp"
[IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
if ($hadLoadFile) { [IO.File]::WriteAllBytes((Join-Path $outputDirectory 'dlc_load.original.json'), $previousBytes) }
$loadedConfig = if ($hadLoadFile) { [Text.Encoding]::UTF8.GetString($previousBytes) | ConvertFrom-Json } else { [pscustomobject]@{} }
$selectedMods = @('mod/ugc_3350890356.mod')
if (-not $ParentOnly) { $selectedMods += 'mod/tfr-estonia.mod' }
if ($ArithmeticQA) {
    if ($ParentOnly) { throw 'ArithmeticQA requires the Estonia submod.' }
    $qaDescriptor = Join-Path $modWorkspace '.cache\engine_qa\descriptor.mod'
    if (-not (Test-Path -LiteralPath $qaDescriptor)) { throw 'Run tools/prepare_engine_qa.py first.' }
    $expectedQaPasses = @(Get-Content -LiteralPath (Join-Path $modWorkspace '.cache\engine_qa\assertions.json') -Raw | ConvertFrom-Json)
    $selectedMods += 'mod/tfr-estonia/.cache/engine_qa/descriptor.mod'
    $kind = 'estonia-qa'
}
$loadedConfig | Add-Member -Force -NotePropertyName enabled_mods -NotePropertyValue $selectedMods
$ownGameProcess = $null
$qaLauncherDescriptor = Join-Path (Split-Path $modWorkspace -Parent) 'tfr-estonia-engine-qa.mod'
$hadQaLauncherDescriptor = Test-Path -LiteralPath $qaLauncherDescriptor
$oldQaLauncherBytes = if ($hadQaLauncherDescriptor) { [IO.File]::ReadAllBytes($qaLauncherDescriptor) } else { $null }
try {
    if ($ArithmeticQA) {
        Copy-Item -LiteralPath (Join-Path $modWorkspace '.cache\engine_qa\descriptor.mod') -Destination $qaLauncherDescriptor
        $selectedMods[-1] = 'mod/tfr-estonia-engine-qa.mod'
        $loadedConfig | Add-Member -Force -NotePropertyName enabled_mods -NotePropertyValue $selectedMods
    }
    [IO.File]::WriteAllText($loadFile, ($loadedConfig | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
    $launchTime = Get-Date
    $ownGameProcess = Start-Process -FilePath $executablePath -ArgumentList @('-debug','-nolauncher') -WorkingDirectory $GameDirectory -WindowStyle Hidden -PassThru
    Write-Output "Started owned HOI4 parser smoke-test process $($ownGameProcess.Id), $kind configuration."
    $deadline = (Get-Date).AddSeconds($Seconds)
    $frontendReady = $false
    $qaFinished = $false
    while ((Get-Date) -lt $deadline) {
        $ownGameProcess.Refresh()
        if ($ownGameProcess.HasExited) { break }
        $liveSetup = Join-Path $profileDirectory 'logs\setup.log'
        $liveGame = Join-Path $profileDirectory 'logs\game.log'
        if ((Test-Path -LiteralPath $liveSetup) -and (Get-Item -LiteralPath $liveSetup).LastWriteTime -ge $launchTime) {
            $frontendReady = [bool](Select-String -LiteralPath $liveSetup -Pattern 'Startup time:' -Quiet)
        }
        if ($ArithmeticQA -and (Test-Path -LiteralPath $liveGame) -and (Get-Item -LiteralPath $liveGame).LastWriteTime -ge $launchTime) {
            $qaFinished = [bool](Select-String -LiteralPath $liveGame -Pattern 'TFR_EST_ENGINE_QA_END' -Quiet)
        }
        if ($frontendReady -and ((-not $ArithmeticQA) -or $qaFinished)) { break }
        Start-Sleep -Seconds 2
    }
    $ownGameProcess.Refresh()
    $processExited = $ownGameProcess.HasExited
    $exitCode = if ($processExited) { $ownGameProcess.ExitCode } else { $null }
    $logDirectory = Join-Path $profileDirectory 'logs'
    if (Test-Path -LiteralPath $logDirectory) {
        foreach ($name in @('error.log','game.log','system.log','setup.log')) {
            $source = Join-Path $logDirectory $name
            if (Test-Path -LiteralPath $source) {
                Copy-Item -LiteralPath $source -Destination (Join-Path $outputDirectory $name)
            }
        }
    }
    $qaPasses = @()
    $qaFailures = @()
    $capturedGameLog = Join-Path $outputDirectory 'game.log'
    if ($ArithmeticQA -and (Test-Path -LiteralPath $capturedGameLog)) {
        $qaPasses = @(Select-String -LiteralPath $capturedGameLog -Pattern 'TFR_EST_ENGINE_QA_PASS (\w+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique)
        $qaFailures = @(Select-String -LiteralPath $capturedGameLog -Pattern 'TFR_EST_ENGINE_QA_FAIL (\w+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique)
    }
    [pscustomobject]@{ processId=$ownGameProcess.Id; parentOnly=[bool]$ParentOnly; arithmeticQA=[bool]$ArithmeticQA; frontendReady=$frontendReady; qaFinished=$qaFinished; qaPasses=$qaPasses; qaFailures=$qaFailures; exited=$processExited; exitCode=$exitCode; durationSeconds=[int]((Get-Date)-$launchTime).TotalSeconds; configuration=$selectedMods; logs=$outputDirectory; campaignStarted=$false } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputDirectory 'result.json') -Encoding utf8
    Write-Output "Saved startup logs to $outputDirectory. This check does not start a campaign."
    if (-not $frontendReady) { throw 'The game did not reach the frontend before the timeout. Inspect the captured logs.' }
    if ($ArithmeticQA -and ($qaPasses.Count -ne $expectedQaPasses.Count -or $qaFailures.Count -ne 0 -or @(Compare-Object $expectedQaPasses $qaPasses).Count -ne 0)) { throw 'Native QA did not pass all expected assertions. Inspect the captured logs.' }
}
finally {
    if ($null -ne $ownGameProcess) {
        $ownGameProcess.Refresh()
        if (-not $ownGameProcess.HasExited) { Stop-Process -Id $ownGameProcess.Id -Force }
    }
    if ($hadLoadFile) { [IO.File]::WriteAllBytes($loadFile, $previousBytes) }
    elseif (Test-Path -LiteralPath $loadFile) { Remove-Item -LiteralPath $loadFile }
    if ($ArithmeticQA) {
        if ($hadQaLauncherDescriptor) { [IO.File]::WriteAllBytes($qaLauncherDescriptor, $oldQaLauncherBytes) }
        elseif (Test-Path -LiteralPath $qaLauncherDescriptor) { Remove-Item -LiteralPath $qaLauncherDescriptor }
    }
    Write-Output 'Restored the original DLC/mod-load configuration.'
}
