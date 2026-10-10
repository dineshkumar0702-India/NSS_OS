# Build the ISO without rebooting Windows

WSL install (`wsl --install`) usually requires a **Windows reboot**. You do **not** need that for OpenNAS-Lite if you use one of the paths below. Your project stays at `C:\Cursor_Projets\NSS_OS`; Cursor chat history is stored separately under your user profile and is not wiped by skipping a reboot.

## Choose a path

| Method | Windows reboot? | Best when |
|--------|-----------------|-----------|
| **A. Debian builder VM** (VMware / VirtualBox) | No | You already use (or will install) VMware for testing |
| **B. GitHub Actions** | No | You want the cloud to compile the ISO |
| **C. Docker Desktop** | Sometimes | Docker is already installed and running |
| **D. WSL** | **Yes** (first time) | Avoid until you can reboot safely |

---

## A. Debian builder VM (recommended on your PC)

Use **one small Linux VM** only to run `live-build`. The ISO lands on the shared folder — same path Windows uses for a **second** test VM later.

### 1. Create a Debian 12 VM (one-time, ~15 minutes)

1. Download [Debian netinst amd64](https://www.debian.org/CD/netinst/) ISO.
2. New VM: **2 vCPU**, **4 GB RAM**, **40 GB** disk, NAT network.
3. Install Debian (minimal system; enable **SSH server** optional).
4. Install VMware Tools or VirtualBox Guest Additions (for shared folders).

### 2. Share the project folder

**VMware Workstation**

- VM → Settings → Options → **Shared Folders** → Add  
  Host path: `C:\Cursor_Projets\NSS_OS`  
  Name: `NSS_OS`  
  Enable “Map as network drive” if offered.

In the guest (Debian), mount is often:

`/mnt/hgfs/NSS_OS` or `\\vmware-host\Shared Folders\NSS_OS`

**VirtualBox**

- Settings → Shared Folders → Add `C:\Cursor_Projets\NSS_OS`, name `NSS_OS`, auto-mount.

Guest path is often:

`/media/sf_NSS_OS`

### 3. Run the build inside the guest

```bash
export OPENNAS_REPO=/mnt/hgfs/NSS_OS   # adjust to your mount
cd "$OPENNAS_REPO"
bash build/scripts/debian-guest-build.sh
```

Build time: about **30–90 minutes**. Output on Windows:

`C:\Cursor_Projets\NSS_OS\build\output\opennas-lite-bookworm-amd64.iso`

### 4. Test in a second VM

Create another VM, attach that ISO, install OpenNAS-Lite — see [VMWARE.md](VMWARE.md).

**Performance tip:** Copy `NSS_OS` into the guest home (`cp -a /mnt/hgfs/NSS_OS ~/NSS_OS`) and set `OPENNAS_REPO=~/NSS_OS` if the shared folder is slow.

---

## B. GitHub Actions (no Linux VM on your PC)

Local git is already initialized with an initial commit. Follow **[GITHUB-ISO-BUILD.md](GITHUB-ISO-BUILD.md)** to create the GitHub repo, `git push`, and download the ISO artifact.

---

## C. Docker Desktop

If Docker is installed and the engine is running (no reboot pending):

```bash
bash build/scripts/build-iso-docker.sh
```

From Git Bash or from inside the Debian builder VM.

---

## Keeping context and project state

- **Files:** Everything remains under `C:\Cursor_Projets\NSS_OS`.
- **This chat:** Cursor keeps session transcripts on disk; reopening the project does not delete them.
- **After a future reboot:** WSL remains optional; you can keep using the builder VM or GitHub path.

## Related

- [BUILD.md](BUILD.md) — Linux/WSL details  
- [VMWARE.md](VMWARE.md) — install and test the produced ISO  
