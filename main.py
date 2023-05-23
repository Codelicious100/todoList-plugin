import json

import quart
import quart_cors
from quart import request
import requests


# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

_TODOS = {}

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("ai-plugin.json") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/json")
    
@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return quart.Response(response='OK', status=200)


@app.get("/todo/<string:username>/<string:message>")
async def add_todo1(username,message):
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(message)
    return quart.Response(response='OK', status=200)

 
@app.get("/todos/<string:username>/")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)


@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await quart.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')



@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("alice", f"https://{host}")
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5002)


if __name__ == "__main__":
    main()
    
def call_openai_api(prompt):
    url = "https://api.openai.com/v1/engines/davinci-codex/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer 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"
    }

    data = {
        "prompt": prompt,
        "max_tokens": 100
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()