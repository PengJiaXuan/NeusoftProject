$runIds = @(
    "formal_shadow_rerun_v1",
    "formal_claude_app_max20_v1",
    "formal_gemini_api_vertex_v1"
)

$root = "c:\Users\admin\Desktop\Test\hidden_fork\results\runs"

foreach ($runId in $runIds) {
    $runRoot = Join-Path $root $runId
    Write-Host ""
    Write-Host ("=" * 72)
    Write-Host $runId
    Write-Host ("=" * 72)

    if (-not (Test-Path $runRoot)) {
        Write-Host "missing run directory"
        continue
    }

    $manifest = Join-Path $runRoot "manifest.json"
    if (Test-Path $manifest) {
        try {
            $m = Get-Content $manifest -Raw | ConvertFrom-Json
            Write-Host ("status: " + $m.status)
            if ($m.updated_at_utc) {
                Write-Host ("updated_at_utc: " + $m.updated_at_utc)
            }
            if ($m.last_error) {
                Write-Host ("last_error: " + $m.last_error)
            }
        } catch {
            Write-Host "manifest: unreadable"
        }
    } else {
        Write-Host "manifest: missing"
    }

    foreach ($kind in @("raw", "scored")) {
        $dir = Join-Path $runRoot $kind
        Write-Host ""
        Write-Host ($kind.ToUpper())
        if (-not (Test-Path $dir)) {
            Write-Host "  missing"
            continue
        }
        $files = Get-ChildItem $dir -Filter *.json -ErrorAction SilentlyContinue | Sort-Object Name
        if (-not $files) {
            Write-Host "  no files yet"
            continue
        }
        foreach ($file in $files) {
            try {
                $count = (Get-Content $file.FullName -Raw | ConvertFrom-Json).Count
                Write-Host ("  {0}: {1}" -f $file.Name, $count)
            } catch {
                Write-Host ("  {0}: unreadable" -f $file.Name)
            }
        }
    }
}
