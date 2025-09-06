# AllahWare R6

https://github.com/ttenacityy/AllahWare-R6/issues/1#issue-3389129786

A recoil-control app for Rainbow Six Siege.

## ⚡ Core Features

- 🎯 **Recoil Control** – Adjustable vertical and horizontal recoil per-operator.
- 👥 **Operator Profiles** – Separate configs for Attackers and Defenders.
- ⚙️ **Config Saving** – Per-operator configs automatically saved and loaded.
- 🖱️ **Autoclicker** – Choose CPS (Clicks Per Second) and bind any mouse button
- 🔄 **Auto-Update Check** – On launch, checks GitHub for the latest version and notifies you if an update is available.
- 🛡️ **Completely External** – Does not touch, read, or write the game’s memory; it only simulates standard mouse input at the OS level.
  
## 📂 Config Storage

Configs are saved in:  
`C:\AllahWare\operator_configs`  

Each operator has its own `.cfg` file storing the recoil values you set in the UI.

---

## 🔐 Note

An `.exe` version is also available, built with PyInstaller.  

If you want to verify the safety of the exe build:  
You are welcome to upload it to VirusTotal or run it inside tria.ge sandbox.  

Since this is a personal project, false positives may occur (because of PyInstaller), but you’re free to review the Python source here on GitHub.

---

📬 Contact: `@boning` on Discord if you have any questions or want to report any issues.
