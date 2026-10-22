$ErrorActionPreference = 'Stop'
$refs = @(
    @('kaja_kallas','Kaja Kallas','Kaja Kallas (crop).jpg'),
    @('juri_ratas','Jüri Ratas','Jüri Ratas 2017-05-25 (cropped).jpg'),
    @('kristen_michal','Kristen Michal','Kristen Michal 2023 (cropped).jpg'),
    @('tanel_kiik','Tanel Kiik','Tanel Kiik (crop).jpg'),
    @('mihhail_kolvart','Mihhail Kõlvart','Mihhail Kõlvart Pätsi monumendi avamisel. 2022 (cropped).jpg'),
    @('helir_valdor_seeder','Helir-Valdor Seeder','Helir-Valdor Seeder 2016.jpg'),
    @('indrek_saar','Indrek Saar','Indrek-saar-luna-lazzarini-1.png'),
    @('kristina_kallas','Kristina Kallas','Kristina Kallas KF (cropped).jpg'),
    @('lavly_perling','Lavly Perling','Lavly Perling 2021-10-14 (cropped).jpg'),
    @('lauri_laanemets','Lauri Läänemets','Lauri Läänemets at the Opinion Festival 2022 in Paide, Estonia (cropped).jpg')
)
$headers = @{'User-Agent'='TFR-Estonia-Artwork/1.0 (local game art research)'}
$titles = ($refs | ForEach-Object { 'File:' + $_[2] }) -join '|'
$api = 'https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles=' + [uri]::EscapeDataString($titles)
$pages = (Invoke-RestMethod -Uri $api -Headers $headers).query.pages.PSObject.Properties.Value
$manifest = @()
foreach ($ref in $refs) {
    $page = $pages | Where-Object { $_.title -eq ('File:' + $ref[2]) } | Select-Object -First 1
    $info = $page.imageinfo[0]
    $original = ($info.url -split '\?')[0]
    $base = $original.Replace('https://upload.wikimedia.org/wikipedia/commons/','https://thumb.wikimedia.org/wikipedia/commons/thumb/')
    $filename = ($original -split '/')[-1]
    $download = $base + '/960px-' + $filename
    $ext = [IO.Path]::GetExtension($ref[2]).ToLower()
    $path = Join-Path $PSScriptRoot ($ref[0] + $ext)
    Invoke-WebRequest -Uri $download -Headers $headers -OutFile $path -UseBasicParsing
    $manifest += [ordered]@{
        person=$ref[0]; name=$ref[1]; source_page_url=$info.descriptionurl
        direct_image_url=$original; downloaded_image_url=$download
        local_path=('docs/artwork/ministers/references/'+$ref[0]+$ext)
        author=$info.extmetadata.Artist.value; license=$info.extmetadata.LicenseShortName.value
        license_url=$info.extmetadata.LicenseUrl.value; date=$info.extmetadata.DateTimeOriginal.value
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'sources_pm.json') -Encoding utf8
    Write-Output ('Saved '+$ref[0])
}
