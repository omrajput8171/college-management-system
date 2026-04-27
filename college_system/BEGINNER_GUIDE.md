# 🎓 Beginner Guide: Build Your First Flask Website

> **Time needed:** 1–2 hours  
> **Level:** Complete beginner  
> **Goal:** Build a simple working website using Python Flask

---

## Step 1: Create Project Folder

Create a new folder (directory) on your computer. Name it:

```
college_system
```

> **Tip:** Do not use spaces in the folder name. Use underscore `_` instead.

---

## Step 2: Create Project Structure

Inside the `college_system` folder, create this structure:

```
college_system/
├── app.py
└── templates/
    └── index.html
```

### How to create:
1. Create a file named `app.py`
2. Create a folder named `templates`
3. Inside `templates`, create a file named `index.html`

> **Tip:** The folder name `templates` must be spelled exactly like this. Flask looks for this name automatically.

---

## Step 3: Write Flask Backend Code

Open `app.py` and type this code:

```python
# import Flask and render_template
from flask import Flask, render_template

# create the app
app = Flask(__name__)

# create route for home page
@app.route('/')
def home():
    return render_template('index.html')

# run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
```

### What this code does:
- `Flask(__name__)` → creates your web app
- `@app.route('/')` → tells the app what to show at the home page
- `render_template('index.html')` → shows the HTML page
- `debug=True` → if you change code, the server restarts automatically

> **Tip:** Do not forget the `@` symbol before `app.route`. It is called a decorator.

---

## Step 4: Write HTML Frontend

Open `templates/index.html` and type this code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>College Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f8ff;
            text-align: center;
        }
        .container {
            margin-top: 100px;
        }
        h1 {
            color: #333;
        }
        p {
            color: #555;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to College Management System</h1>
        <p>This is a simple Flask website built by a beginner.</p>
    </div>
</body>
</html>
```

> **Tip:** Save the file with the name exactly `index.html`. If the name is wrong, Flask will show an error.

---

## Step 5: Run the Project

Open **Terminal** inside VS Code (press `` Ctrl + ` ``) or open Command Prompt.

Go inside the `college_system` folder:

```bash
cd college_system
```

Run this command:

```bash
python app.py
```

> **Tip:** Make sure you are inside the `college_system` folder before running the command.

---

## Step 6: Open in Browser

Open any web browser (Chrome, Edge, Firefox) and go to:

```
http://127.0.0.1:5000
```

Or type:

```
http://localhost:5000
```

---

## Step 7: Expected Output

You will see a webpage with:

- **Heading:** Welcome to College Management System
- **Paragraph:** This is a simple Flask website built by a beginner.

If you see this, congratulations — your Flask website is working! 🎉

---

## Step 8: Common Errors and Solutions

### ❌ Error 1: `Flask not installed`

**Message:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:** Install Flask using this command:
```bash
pip install flask
```

> **Tip:** If `pip` does not work, try `pip3 install flask`.

---

### ❌ Error 2: `Python not recognized`

**Message:**
```
'python' is not recognized as an internal or external command
```

**Solution:** Python is not added to your system PATH. You need to:
1. Reinstall Python
2. During setup, check the box "Add Python to PATH"

---

### ❌ Error 3: `Template not found`

**Message:**
```
jinja2.exceptions.TemplateNotFound: index.html
```

**Solution:** Check these things:
- Folder name must be exactly `templates` (all small letters)
- `index.html` must be inside the `templates` folder
- `index.html` spelling must be correct

---

## ✅ Quick Checklist Before Running

- [ ] Folder name is `college_system`
- [ ] `app.py` is created
- [ ] `templates` folder is created (spelling exact)
- [ ] `index.html` is inside `templates`
- [ ] Flask is installed (`pip install flask`)
- [ ] You are inside the `college_system` folder in terminal

---

## 🚀 Next Steps You Can Try

- Add more pages like `/about` or `/contact`
- Add a navigation menu
- Add a form to collect student information

---

**Happy Coding! 🎓**

