from flask import Flask
from flask import request, redirect
app = Flask(__name__)

index_html = '''
<form action="/signup" method="post">
  <input type="text" name="email"></input>
  <input type="submit" value="Signup"></input>
</form>
'''

@app.route('/signup', methods = ['POST'])
def signup():
    email = request.form['email']
    print("The email address is '" + email + "'")
    return redirect('/')

@app.route('/')
def hello_world():
    return index_html#'Hello, World!'

