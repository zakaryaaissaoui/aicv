# Quick Fix for VS Code Terminal on Windows

## 🚀 Solution: Use Command Prompt in VS Code Instead of PowerShell

### Step 1: Change Default Terminal in VS Code

1. Press `Ctrl + Shift + P` to open Command Palette
2. Type: `Terminal: Select Default Profile`
3. Choose **Command Prompt** instead of PowerShell
4. Close the current terminal (X button)
5. Open a new terminal: `Ctrl + Backtick` or Terminal > New Terminal

### Step 2: Run These Commands in Command Prompt

```cmd
cd aicv
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python test_parser_and_search.py
```

---

## ✅ Alternative: Fix PowerShell in VS Code

If you want to keep using PowerShell:

### Step 1: Open PowerShell as Administrator
- Close VS Code completely
- Right-click VS Code > Run as Administrator
- Reopen your project

### Step 2: Run in Terminal
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
cd aicv
rmdir /s /q venv
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python test_parser_and_search.py
```

---

## 🎯 I Recommend: Use Command Prompt

**Why?** It's simpler on Windows and avoids execution policy issues.

**Steps:**
1. `Ctrl + Shift + P` in VS Code
2. Search: `Terminal: Select Default Profile`
3. Choose **Command Prompt**
4. Close terminal, open new one
5. Copy-paste the command block above

---

## ✨ What Your Project Already Has

Looking at your screenshot, I can see:
- ✅ `parser_engine.py` - Multi-sector parser
- ✅ `search_engine.py` - Intelligent search
- ✅ `requirements.txt` - Dependencies listed
- ✅ `main.py` - Entry point
- ✅ `database.py` - Database layer
- ✅ Full folder structure ready

**You're 90% there!** Just need to activate venv and install dependencies.

---

## 🔧 Try This NOW

Copy and paste into your **Command Prompt** terminal in VS Code:

```cmd
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Then run:
```cmd
python test_parser_and_search.py
```

Let me know if you hit any errors! 🚀
