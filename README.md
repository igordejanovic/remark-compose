# remark-compose

[Remark](https://remarkjs.com/) slide builder.

## What does it do?

- Generates remark slides from HTML template and markdown files.
- Live server that watch for changes in template and markdown files and 
  do output HTML regeneration. 

## Why?

- I like to edit remark slides in pure markdown files without HTML container
  clutter. That way I can concentrate on slides content.
- I like to change my remark configuration and HTML container in one place and
  have it consistently applied to all my slides.


## Installation


    $ pip install https://github.com/igordejanovic/remark-compose/archive/master.zip


## Usage

Write `myconf.rconf` file. Rconf is a DSL for generator configuration consisting
of `template` path and a set of rules.

      template "path/to/template.html"

      "input/firstfile.md"
        title = "Title for first slide"

      "input/secondfile.md" => "output/second_file_with_custom_out_name.html"
        title = "Title for second slide"

      "input2/*.md" => "output/"
        custom_param = "Some value"


Each `.rconf` rule defines input file (or [glob2
pattern](https://github.com/miracle2k/python-glob2/)) and optionally output
file. If output file is not given it will default to the same directory and
same base name but '.html' extension. Output can be directory in which case
full output name is created by adding the base name of the input and '.html'
extension.

Each rule may contains arbitrary number of additional parameters to the
template. E.g. in previous example we use it for `title` and `custom_param`.
These params will be passed to template context.

In `myconf.rconf` specify path to HTML template. The content of `.md` files will
be rendered at the place of `{{content}}` tag inside HTML template.

For example, HTML template might look like:

```html
<!DOCTYPE html>
<html>
    <head>
    <title>{{title}}</title>
    <meta charset="utf-8">
    <style>
        @import url(https://fonts.googleapis.com/css?family=Yanone+Kaffeesatz);
        @import url(https://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic);
        @import url(https://fonts.googleapis.com/css?family=Ubuntu+Mono:400,700,400italic);

        body { font-family: 'Droid Serif'; }
        h1, h2, h3 {
        font-family: 'Yanone Kaffeesatz';
        font-weight: normal;
        }
        .remark-code, .remark-inline-code { font-family: 'Ubuntu Mono'; }
    </style>
    </head>
    <body>
    <textarea id="source">

{{content}}

    </textarea>
    <script src="https://gnab.github.io/remark/downloads/remark-latest.min.js">
    </script>
    <script>
        var slideshow = remark.create();
    </script>
    </body>
</html>
```




Now, to rebuild your HTML files run:

    $ remarkc build myconf


To start live server:

    $ remarkc serve myconf


For help:

    $ remarkc --help


or:

    $ remarkc serve --help


# Note

Although it is motivated by remark slides it doesn't depend on remark in any
way. You can use it for merging arbitrary files.

## LICENSE

MIT

