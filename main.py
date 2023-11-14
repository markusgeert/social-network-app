from flask import Flask, render_template, request

app = Flask(__name__)

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/message')
def message():
    print(request.form['message'])

    return render_template('message.html', message=request.form['message'])

@app.get('/admin')
def admin():
    return render_template('admin.html')
