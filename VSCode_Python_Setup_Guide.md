# VS Code Python Setup Guide

A quick beginner-friendly guide to configure VS Code and run your first Python and Flask projects.

---

## Step 4: Select Python Interpreter

1. Open **Command Palette**: Press `Ctrl + Shift + P`
2. Type: `Python: Select Interpreter`
3. Click on **Python: Select Interpreter** from the list
4. Choose **Python 3.13** (or whichever version is installed on your system)
   - If you don’t see your version, make sure Python is installed

> **Tip:** The interpreter tells VS Code which Python version to use for running your code.

---

## Step 5: Create and Run a Test File

1. **Create a new file**: Click `New File...` in the Explorer panel (or press `Ctrl + N`)
2. **Save it as**: `test.py`
3. **Add this code** inside `test.py`:

   ```python
   print("VS Code Ready!")
   ```

4. **Run the file** using either of the methods below:
   - **Method A:** Click the ▶️ **Run button** at the top-right of the editor
   - **Method B:** Open terminal (`Ctrl + \``) and type:
     ```bash
     python test.py
     ```
5. **Expected output** in the terminal:
   ```
   VS Code Ready!
   ```

---

## Step 6: Run a Flask Project

1. **Place your `app.py` file** inside your project folder (same folder as `test.py` or your main workspace)
2. **Open Terminal in VS Code**: Press `Ctrl + \``
3. **Run the Flask app** by typing:
   ```bash
   python app.py
   ```
4. **Open your browser** and go to:
   ```
   http://127.0.0.1:5000
   ```
   - You should see your Flask application running!

> **Tip:** If Flask is not installed, run `pip install flask` in the terminal first.

---

## ✅ Quick Checklist

| Task | Status |
|------|--------|
| Python interpreter selected | ☐ |
| `test.py` created and prints "VS Code Ready!" | ☐ |
| Flask app running on `http://127.0.0.1:5000` | ☐ |

---

## Need Help?

- **Interpreter not showing?** Restart VS Code after installing Python.
- **Python not recognized?** Add Python to your system PATH during installation.
- **Flask errors?** Make sure you installed it with `pip install flask`.

