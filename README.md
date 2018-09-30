# Tequilla Template Engine

## Installation

```shell
pip install https://github.com/effordsbeard/tequilla/archive/master.zip
```

## Creating templates

```html
<body>
    <div class="post" loop="post in data.posts">
        <div class="author" if="post.author">
            {{post.author}}
        </div>
        <div class="text">
            {{post.html}}
        </div>
        <div class="comments" loop="comment in post.comments">
            {{comment.text}}
        </div>
    </div>
</body>
```

## Templates structure

* templates
    * compiled [auto created folder for keeping python functions]
        * index.html.py
    * index.html.tpl

## Initialization

```python
    import tequilla

    t = tequilla('templates')
    t.compile()  # this method creates .py files in 'compiled' folder and imports render functions to memory

    res = t.render('index.html.tpl', data)  # provide render function with relative path to template

    print(res)

```


## Data

**data** param can be any python data structure, you use it in template in your way
For example, if data is dictionary, in templates it will be sth like that:
```
    data['prop']
```
or if it is an object from ORM you can use it like:
```
    data.prop
```
or you can create namespaces from dict

## Including

you can include template files with #include directive

modules/head.html.tpl
```html
    <head>
        <meta name="viewport" content="width=device-width">
        <link rel="stylesheet" href="styles.css">
    </head>
```

index.html.tpl
```html
    <html>
        #include modules/head.html.tpl
        <body>
        </body>
    </html>
```

## For loops

```html
<div loop="items in items">
    {{item}}
</div>
```

## IF statement
```html
<div if="len(items)">
    here is some information about items
</div>
```

IF and FOR statements can be any valid python expressions, in compiled them will be used in real python statements.
