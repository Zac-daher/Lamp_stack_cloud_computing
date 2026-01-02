from flask import Flask
from flask import session, request, redirect, url_for
import mysql.connector
import requests


app = Flask(__name__)
app.secret_key = 'not showing here'

@app.route("/")
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('call_llm'))
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔐 Login</title>
        <style>
            body {
                background-color: #111;
                color: #eee;
                font-family: 'Segoe UI', sans-serif;
                padding: 40px;
                max-width: 600px;
                margin: auto;
            }
            h2 {
                color: #00ffc8;
                text-align: center;
            }
            form {
                margin-top: 30px;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                font-size: 1em;
                border-radius: 6px;
                border: 1px solid #444;
                background: #222;
                color: #eee;
            }
            input[type="submit"] {
                margin-top: 15px;
                padding: 10px 25px;
                font-size: 1em;
                background: #00ffc8;
                color: #111;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background: #00dab0;
            }
        </style>
    </head>
    <body>
        <h2>Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Enter your username" required>
            <input type="submit" value="Login 🔑">
        </form>
    </body>
    </html>
    '''
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         return redirect(url_for('index'))
#     return '''
#         <form method="post">
#             <p><input type=text name=username>
#             <p><input type=submit value=Login>
#         </form>
#     '''
@app.route('/logout')
def logout():
    session.pop('username', None)
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>👋 Logged Out</title>
        <style>
            body {
                background-color: #111;
                color: #eee;
                font-family: 'Segoe UI', sans-serif;
                padding: 40px;
                max-width: 600px;
                margin: auto;
                text-align: center;
            }
            h2 {
                color: #00ffc8;
            }
            a {
                color: #00ffc8;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h2>You have been logged out.</h2>
        <p><a href="/login">Login again</a></p>
        <p><a href="/">Return to home</a></p>
    </body>
    </html>
    '''


@app.route("/dbtest")
def dbtest():
    try:
        connection = mysql.connector.connect(
            host="db",            
            user="root",
            password="example",
            database="mydatabase"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT user_prompt, llm_response FROM interactions ORDER BY id DESC LIMIT 5")
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if not results:
            return "No interactions found."

        # Build rows for each interaction
        rows_html = ""
        for prompt, response in results:
            rows_html += f"""
            <div class="interaction">
                <div class="label">Prompt:</div>
                <div class="bubble">{prompt}</div>
                <div class="label">Response:</div>
                <div class="bubble">{response}</div>
            </div>
            <hr>
            """

        # Full styled page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🧠 Interaction History</title>
            <style>
                body {{
                    background-color: #111;
                    color: #eee;
                    font-family: 'Segoe UI', sans-serif;
                    padding: 40px;
                    max-width: 800px;
                    margin: auto;
                }}
                h1 {{
                    color: #00ffc8;
                    text-align: center;
                    font-size: 2em;
                    margin-bottom: 30px;
                }}
                .interaction {{
                    margin-bottom: 30px;
                }}
                .label {{
                    font-weight: bold;
                    color: #00ffc8;
                    margin-top: 10px;
                    margin-bottom: 5px;
                }}
                .bubble {{
                    background: #222;
                    color: #eee;
                    border: 1px solid #444;
                    border-radius: 10px;
                    padding: 15px;
                    white-space: pre-wrap;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid #333;
                    margin: 30px 0;
                }}
            </style>
        </head>
        <body>
            <h1>🧠 Last 5 Interactions</h1>
            {rows_html}
        <p style="text-align:center;">
            <a href="/logout" style="color: #00ffc8; font-weight: bold;">🚪 Log Out</a>
        </p>
        <p style="text-align:center;">
            <a href="/llmtest" style="color: #00ffc8; font-weight: bold;">🏠 Back to LLM Home</a>
        </p>
        </body>
        </html>
        """
    except Exception as e:
        return f"MySQL connection failed: {e}"
#chat gpt assisted me in generating the html code for all,
# and structuring the database tables along with implementing the tables into my code. 
#attached is the conversation,
#I was running into problems with the llm connection and asked chat to help,
#but I ended up figuring out how to redownload the slm and worked using my old code
#attached is the conversation; I only used the html and the database code.
# https://chatgpt.com/c/681a9c02-f54c-800e-a709-3792f3c2e679

@app.route("/llmtest", methods=["GET", "POST"])
def call_llm():
    llm_output = ""
    prompt = ""
    if request.method == "POST":
        prompt = request.form.get('prompt', '').strip()

        if not prompt:
            llm_output = "come onnnnnnnnnnn No prompt entered."
        else:
            try:
                headers = {"Content-Type": "application/json"}
                response = requests.post("http://ollama:11434/api/generate", headers=headers, json={
                    "model": "tinyllama",
                    "prompt": prompt,
                    "stream": False
                })
                response.raise_for_status()
                llm_output = response.json().get('response', ' No response received.')

                # INSERT INTO DB
                connection = mysql.connector.connect(
                    host="db",
                    user="root",
                    password="example",
                    database="mydatabase"
                )
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO interactions (user_prompt, llm_response) VALUES (%s, %s)",
                    (prompt, llm_output)
                )
                connection.commit()
                cursor.close()
                connection.close()

                print("✅ Inserted into database:", prompt, llm_output)

            except Exception as e:
                llm_output = f"nopeeeeeee Error: {e}"

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>⚡ employee generAItor</title>
        <style>
            body {{
                background-color: #111;
                color: #eee;
                font-family: 'Segoe UI', sans-serif;
                padding: 40px;
                max-width: 800px;
                margin: auto;
            }}
            h1 {{
                color: #00ffc8;
                font-size: 2em;
                text-align: center;
                margin-bottom: 30px;
            }}
            textarea {{
                width: 100%;
                background: #222;
                color: #eee;
                border: 1px solid #444;
                border-radius: 10px;
                padding: 10px;
                font-size: 1em;
                resize: vertical;
            }}
            input[type="submit"] {{
                margin-top: 10px;
                padding: 10px 25px;
                font-size: 1em;
                background: #00ffc8;
                color: #111;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: background 0.3s ease;
            }}
            input[type="submit"]:hover {{
                background: #00dab0;
            }}
            .response {{
                margin-top: 30px;
                padding: 20px;
                background: #1a1a1a;
                border-radius: 10px;
                border: 1px solid #333;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <h1>⚡ employee generAItor</h1>
        <form method="post">
            <textarea name="prompt" rows="4" placeholder="Lets make your agent!!!!!!!! Enter what you want. I can make anything...">{prompt}</textarea>
            <br>
            <input type="submit" value="Submit 🔥" />
        </form>
        <div class="response">
            <strong>LLM Response:</strong><br>{llm_output}
        </div>
    <p style="text-align:center; margin-top: 20px;">
        <a href="/dbtest" style="color: #00ffc8; font-weight: bold;">📄 View Previous Interactions</a>
    </p>
    </body>
    </html>
    '''

