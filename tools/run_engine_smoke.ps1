param(
    [ValidateRange(30,600)][int]$Seconds = 120,
    [switch]$ParentOnly,
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
$kind = if ($ParentOnly) { 'parent' } else { 'estonia' }
$outputDirectory = Join-Path $modWorkspace "test-output\engine-$kind-$stamp"
[IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
if ($hadLoadFile) { [IO.File]::WriteAllBytes((Join-Path $outputDirectory 'dlc_load.original.json'), $previousBytes) }
$loadedConfig = if ($hadLoadFile) { [Text.Encoding]::UTF8.GetString($previousBytes) | ConvertFrom-Json } else { [pscustomobject]@{} }
$selectedMods = @('mod/ugc_3350890356.mod')
if (-not $ParentOnly) { $selectedMods += 'mod/tfr-estonia.mod' }
$loadedConfig | Add-Member -Force -NotePropertyName enabled_mods -NotePropertyValue $selectedMods
$ownGameProcess = $null
try {
    [IO.File]::WriteAllText($loadFile, ($loadedConfig | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
    $ownGameProcess = Start-Process -FilePath $executablePath -ArgumentList @('-debug','-nolauncher') -WorkingDirectory $GameDirectory -WindowStyle Hidden -PassThru
    Write-Output "Started owned HOI4 parser smoke-test process $($ownGameProcess.Id), $kind configuration."
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        $ownGameProcess.Refresh()
        if ($ownGameProcess.HasExited) { break }
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
    [pscustomobject]@{ processId=$ownGameProcess.Id; parentOnly=[bool]$ParentOnly; exited=$processExited; exitCode=$exitCode; durationSeconds=$Seconds; configuration=$selectedMods; logs=$outputDirectory; campaignStarted=$false } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputDirectory 'result.json') -Encoding utf8
    Write-Output "Saved startup logs to $outputDirectory. This check does not start a campaign."
}
finally {
    if ($null -ne $ownGameProcess) {
        $ownGameProcess.Refresh()
        if (-not $ownGameProcess.HasExited) { Stop-Process -Id $ownGameProcess.Id -Force }
    }
    if ($hadLoadFile) { [IO.File]::WriteAllBytes($loadFile, $previousBytes) }
    elseif (Test-Path -LiteralPath $loadFile) { Remove-Item -LiteralPath $loadFile }
    Write-Output 'Restored the original DLC/mod-load configuration.'
}
