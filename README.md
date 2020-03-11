# godotdocset
Dash docset generator for Godot engine xml docs

Depends on jinja2

```
usage: godotdocset.py [-h] -f FROM

optional arguments:
  -h, --help            show this help message and exit
  -f FROM, --from FROM  folder or xml file
```

Generating docset:
0. Install all deps: `pip3 install jinja2`
1. Go to https://github.com/godotengine/godot/
2. Get doc/classes directory somehow (clone entire repo)
3. Run generator `python3 godotdocset.py -f ./classes`

There is Godot.docset.7z file in the project with precompiled docset.
