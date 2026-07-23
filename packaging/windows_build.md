# Windows Build

User: 
Do you know if a build for Windows can be created using a EC2 Instance?

Assistant: 
Yes. A **Windows build can be created on an EC2 Windows instance**, and for PyInstaller that is usually the correct approach.

Like macOS, PyInstaller builds are generally **OS-specific**:

| Target build        | Build machine should be |
|---------------------|-------------------------|
| Linux               | Linux                   |
| macOS Apple Silicon | macOS Apple Silicon     |
| Windows x64         | Windows x64             |

So for a Windows build, use a **Windows EC2 instance**.

## Recommended EC2 target

For most users, build a standard **Windows x64** executable on:

```text
Windows Server 2022 x64
```

or:

```text
Windows Server 2019 x64
```

A normal EC2 instance type is fine, for example:

```text
t3.large
t3.xlarge
m6i.large
m6i.xlarge
```

I’d use at least:

```text
2 vCPU / 8 GB RAM
```

because PyInstaller plus PySide6, spaCy, NumPy, SciPy, and pandas can be memory-heavy.

## High-level workflow

1. Launch a Windows EC2 instance.
2. Connect with Remote Desktop.
3. Install Git.
4. Install Miniforge or Miniconda for Windows x64.
5. Clone/copy the project.
6. Create the conda build environment.
7. Install the project.
8. Run PyInstaller.
9. Test the `.exe`.
10. Zip the full `dist/lmda-app` folder.

## Recommended Windows build steps

### 1. Install Miniforge or Miniconda

For Windows x64, Miniforge is a good choice:

```text
Miniforge3-Windows-x86_64.exe
```

Install it for your user account.

Then open:

```text
Miniforge Prompt
```

or:

```text
Anaconda Prompt
```

## 2. Clone the project

```powershell
git clone <your-repo-url>
cd cl_st1_gelc_lmda
```

Or copy the project onto the instance.

## 3. Create the build environment

```powershell
conda env create -f env\condaenv-build.yaml
conda activate cl_st1_gelc_lmda_build
```

If it already exists:

```powershell
conda env update -f env\condaenv-build.yaml --prune
conda activate cl_st1_gelc_lmda_build
```

## 4. Install the project

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Optional source smoke test:

```powershell
python -m lmda_app
```

## 5. Build with PyInstaller

Use the same narrowed PySide6 strategy:

```bat
pyinstaller ^
  --name lmda-app ^
  --windowed ^
  --clean ^
  --noconfirm ^
  --paths src ^
  --collect-all spacy ^
  --collect-all en_core_web_sm ^
  --hidden-import en_core_web_sm ^
  --exclude-module PySide6.QtWebEngineCore ^
  --exclude-module PySide6.QtWebEngineWidgets ^
  --exclude-module PySide6.QtWebEngineQuick ^
  --exclude-module PySide6.QtWebChannel ^
  src\lmda_app\main.py
```

This should produce something like:

```text
dist\lmda-app\
  lmda-app.exe
  _internal\
```

## 6. Test the Windows build

From Anaconda Prompt:

```bat
.\dist\lmda-app\lmda-app.exe
```

Run your smoke test:

- app opens;
- project can be created/opened;
- corpus validation works;
- downstream outputs are created.

## 7. Package the Windows build

As with Linux, do **not** copy only the `.exe`. Copy or zip the whole folder. In Anaconda Prompt, if PowerShell is available, you can call it explicitly:

```bat
powershell -Command "Compress-Archive -Path .\dist\lmda-app -DestinationPath .\dist\lmda-app-windows-x86_64.zip -Force"
```

Or you can right-click the `dist\lmda-app` folder in File Explorer and choose **Send to → Compressed zipped folder**.

Distribute:

```text
dist\lmda-app-windows-x64.zip
```

Users will unzip it and run:

```text
lmda-app\lmda-app.exe
```

## Notes about Windows security warnings

Unsigned Windows executables may trigger Microsoft Defender SmartScreen warnings, especially when downloaded from the internet.

For internal testing, this is usually acceptable. For broader public distribution, you may eventually want:

- Authenticode code signing certificate;
- signed executable;
- possibly an installer such as Inno Setup or WiX.

## Short answer

Yes — use a **Windows x64 EC2 instance**, run the same conda/PyInstaller workflow there, and distribute the entire:

```text
dist\lmda-app\
```

folder as a zip.