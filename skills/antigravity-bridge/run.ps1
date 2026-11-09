# AgyBridge task body. Reads job.json from its own folder, runs agy inside
# the logged-in user's session (where the Antigravity sign-in works), and
# writes out.txt / err.txt / done.txt next to itself.
$base = $PSScriptRoot
Remove-Item "$base\done.txt","$base\out.txt","$base\err.txt" -ErrorAction SilentlyContinue
$job = Get-Content "$base\job.json" -Raw | ConvertFrom-Json
$agy = Join-Path $env:LOCALAPPDATA 'agy\bin\agy.exe'
if ($job.workdir) { Set-Location $job.workdir }
if ($job.kind -eq 'command') {
  $argList = @($job.args)
  & $agy @argList > "$base\out.txt" 2> "$base\err.txt"
} else {
  $extra = @()
  if ($job.model) { $extra += @('--model', $job.model) }
  if ($job.effort) { $extra += @('--effort', $job.effort) }
  if ($job.mode) { $extra += @('--mode', $job.mode) }
  & $agy -p $job.prompt --print-timeout 600s --dangerously-skip-permissions @extra > "$base\out.txt" 2> "$base\err.txt"
}
foreach ($f in 'out.txt','err.txt') { $p = Join-Path $base $f; if (Test-Path $p) { $c = Get-Content $p -Raw; if ($c) { $c | Set-Content $p -Encoding UTF8 } } }
"$LASTEXITCODE" | Out-File "$base\done.txt" -Encoding ascii
