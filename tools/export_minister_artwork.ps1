param([switch]$Check)

# Technical export of imagegen artwork; no creative transformation is performed here.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent
$art = Join-Path $root 'docs/artwork/ministers'
$icons = Join-Path $root 'gfx/interface/ideas/EST/ministers'
$portraits = Join-Path $root 'gfx/leaders/EST/ministers'
$names = [ordered]@{}
foreach ($file in @('minister_roster_established.json','minister_roster_newer.json')) {
    foreach ($candidate in (Get-Content -LiteralPath (Join-Path $PSScriptRoot $file) -Raw | ConvertFrom-Json)) {
        $names[$candidate.person] = $candidate.name
    }
}
foreach ($person in (Get-Content -LiteralPath (Join-Path $art 'sources.json') -Raw | ConvertFrom-Json)) {
    $names[$person.person] = $person.name
}
$executives = @('kaja_kallas','kristen_michal','juri_ratas','tanel_kiik','mihhail_kolvart','mart_helme','martin_helme','helir_valdor_seeder','indrek_saar','lauri_laanemets','kristina_kallas','lavly_perling')

function Export-Png($Source, [string]$Path, [int]$Width, [int]$Height, [switch]$Fit) {
    $bitmap = [Drawing.Bitmap]::new($Width,$Height,[Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.Clear([Drawing.Color]::Transparent)
        $graphics.CompositingMode = [Drawing.Drawing2D.CompositingMode]::SourceCopy
        $graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $dest = [Drawing.Rectangle]::new(0,0,$Width,$Height)
        if ($Fit) {
            $scale = [Math]::Min($Width/$Source.Width,$Height/$Source.Height)
            $w = [int][Math]::Round($Source.Width*$scale)
            $h = [int][Math]::Round($Source.Height*$scale)
            $dest = [Drawing.Rectangle]::new([int](($Width-$w)/2),[int](($Height-$h)/2),$w,$h)
        }
        $graphics.DrawImage($Source,$dest)
        $bitmap.Save($Path,[Drawing.Imaging.ImageFormat]::Png)
    } finally { $graphics.Dispose(); $bitmap.Dispose() }
}

function Assert-Png([string]$Path, [int]$Width, [int]$Height) {
    $image = [Drawing.Bitmap]::new($Path)
    try {
        if ($image.Width -ne $Width -or $image.Height -ne $Height) { throw "Wrong dimensions: $Path" }
        if ($image.GetPixel(0,0).A -ne 0 -or $image.GetPixel($Width-1,$Height-1).A -ne 0) { throw "Opaque outside corners: $Path" }
        if ($image.GetPixel([int]($Width/2),[int]($Height/2)).A -lt 250) { throw "Missing portrait center: $Path" }
    } finally { $image.Dispose() }
}

if (-not $Check) {
    New-Item -ItemType Directory -Force -Path $icons,$portraits | Out-Null
    foreach ($person in $names.Keys) {
        $master = [Drawing.Image]::FromFile((Join-Path $art "masters/$person.png"))
        try {
            Export-Png $master (Join-Path $icons "$person.png") 62 67
            if ($person -in $executives) { Export-Png $master (Join-Path $portraits "$person.png") 156 210 -Fit }
        } finally { $master.Dispose() }
    }
}
foreach ($person in $names.Keys) { Assert-Png (Join-Path $icons "$person.png") 62 67 }
foreach ($person in $executives) { Assert-Png (Join-Path $portraits "$person.png") 156 210 }

if (-not $Check) {
    foreach ($factor in @(1,2)) {
        $cellWidth = 145
        $cellHeight = 67*$factor+48
        $rows = [int][Math]::Ceiling($names.Count/8)
        $sheet = [Drawing.Bitmap]::new(8*$cellWidth,$rows*$cellHeight+46)
        $graphics = [Drawing.Graphics]::FromImage($sheet)
        $font = [Drawing.Font]::new('Arial',10)
        $format = [Drawing.StringFormat]::new()
        $format.Alignment = [Drawing.StringAlignment]::Center
        try {
            $graphics.Clear([Drawing.Color]::FromArgb(34,35,42))
            $graphics.DrawString("TFR ESTONIA - 48 minister portraits - ${factor}x game size",$font,[Drawing.Brushes]::White,15,14)
            $graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
            $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::Half
            $index = 0
            foreach ($person in $names.Keys) {
                $x = ($index%8)*$cellWidth
                $y = [int][Math]::Floor($index/8)*$cellHeight+46
                $image = [Drawing.Image]::FromFile((Join-Path $icons "$person.png"))
                try { $graphics.DrawImage($image,[Drawing.Rectangle]::new($x+[int](($cellWidth-62*$factor)/2),$y,62*$factor,67*$factor)) }
                finally { $image.Dispose() }
                $rect = [Drawing.RectangleF]::new($x+2,$y+67*$factor+6,$cellWidth-4,38)
                $graphics.DrawString($names[$person],$font,[Drawing.Brushes]::White,$rect,$format)
                $index++
            }
            $sheet.Save((Join-Path $art "contact_sheet_${factor}x.png"),[Drawing.Imaging.ImageFormat]::Png)
        } finally { $graphics.Dispose(); $sheet.Dispose(); $font.Dispose(); $format.Dispose() }
    }
}
Write-Output "Verified $($names.Count) 62x67 icons and $($executives.Count) 156x210 tooltip portraits, with transparent corners and opaque portrait centers."
