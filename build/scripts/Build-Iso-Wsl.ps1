# Build OpenNAS-Lite ISO via WSL (Debian). Run from PowerShell (Admin required for first-time WSL install).
param(
	[string]$Distro = "Debian",
	[string]$RepoPath = "C:\Cursor_Projets\NSS_OS"
)

$ErrorActionPreference = "Stop"

function Test-Wsl {
	try {
		wsl --status 2>$null | Out-Null
		return $true
	} catch {
		return $false
	}
}

if (-not (Test-Wsl)) {
	Write-Host "WSL is not installed."
	Write-Host "WSL first-time setup usually requires a Windows REBOOT."
	Write-Host "To build without rebooting, use:  docs\BUILD-NO-REBOOT.md"
	Write-Host "  (Debian builder VM in VMware, or GitHub Actions)"
	Write-Host ""
	Write-Host "If you can reboot later:  wsl --install -d Debian"
	exit 1
}

$wslRepo = ($RepoPath -replace '\\', '/') -replace '^C:', '/mnt/c'
$cmd = @"
set -e
sudo apt-get update
sudo apt-get install -y live-build debootstrap squashfs-tools xorriso isolinux syslinux-utils git rsync
if command -v npm >/dev/null 2>&1; then
  cd '$wslRepo' && bash build/scripts/prepare-iso-assets.sh
else
  sudo apt-get install -y nodejs npm 2>/dev/null || true
  cd '$wslRepo' && bash build/scripts/prepare-iso-assets.sh
fi
cd '$wslRepo' && sudo bash build/scripts/build-iso.sh
ls -la build/output/*.iso
"@

Write-Host "Building in WSL ($Distro). This takes 30–90 minutes..."
wsl -d $Distro -e bash -lc $cmd
Write-Host "ISO (Windows path): $RepoPath\build\output\opennas-lite-bookworm-amd64.iso"
