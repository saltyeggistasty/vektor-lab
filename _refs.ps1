$html = Get-Content 'G:\vektor-lab(1)\vektor-lab\templates\index.html' -Raw
# umbrella main cards
$ms = [regex]::Matches($html, 'data-umbrella="([a-z0-9_-]+)"\s*\r?\n\s*data-img="([^"]+)"')
Write-Host "--- UMBRELLA cards ---"
foreach ($m in $ms) { Write-Host ($m.Groups[1].Value + " -> " + $m.Groups[2].Value) }
# first tool of each tools grid (acts as main card backdrop on entry)
Write-Host "--- TOOLS grid first card per umbrella ---"
$grids = [regex]::Matches($html, 'wm-grid wm-grid-tools hidden"[^>]*data-umb="([a-z0-9_-]+)"(.*?)</div>', 'Singleline')
foreach ($g in $grids) {
  $first = [regex]::Match($g.Groups[2].Value, 'data-img="([^"]+)"')
  if ($first.Success) { Write-Host ($g.Groups[1].Value + " -> " + $first.Groups[1].Value) }
}
