# remark-compose

[Remark](https://remarkjs.com/) slide builder.

## What does it do?

- Generates remark slides from HTML template and pure markdown files/templates.
- Live server that watch for changes in template and markdown files and do
  output HTML regeneration.
- Generates only what needs to be generated (like GNU make).

## Motivation

- Using markdown inside HTML you lose editor support like syntax highlighting,
  code outline etc. as your file is treated as HTML only. Some editors could be
  configured for multi-content editing but it is usually not that easy.
- I have to maintain a large number of slide decks and want them to be
  consistent and easy to apply style changes to the set as a whole.
- There
  is
  [a configuration option](https://github.com/gnab/remark/wiki#external-markdown) in
  remark for externalizing markdown which solves first issue but you have to
  maintain two files per slide deck which might be a problem if you have a large
  number of slide decks and want them to be consistent.
- Although, you could import all your css and js files in your HTML file and
  centralise style/configuration sooner or later you will have to alter HTML
  directly. And that is painful if you are building a large number of slide
  decks and would like them to be consistent.
- These are problems only if you maintain a large set of slide decks (e.g. for
  teaching courses). If that is not the case than this tool would be probably an
  overkill.
- All input files are treated as [jinja2](http://jinja.pocoo.org/docs/dev/)
  templates with the same context given to the base template file. This means
  that you can use the full power of jinja2 (e.g. template inheritance, see
  examples) and have variables set in `rconf` file. There is a variable `now` in
  the template context of `datetime` type. You can use it to render date/time
  when the slides were built.

  For example:
  
      # {{ title }}
      {% if subtitle %}
      ## {{ subtitle }}
      {% endif %}

      Created on {{now|dtformat("%d.%m.%Y %H:%M")}}

- Although it is motivated by remark it doesn't depend on remark in any way. You
  can use it with other html/javascript slides creation tools.

## Installation

- Create and activate Python virtual environment (recommended):

        $ virtualenv venv        
        New python executable in /home/igor/tmp/rmctest/venv/bin/python3
        Also creating executable in /home/igor/tmp/rmctest/venv/bin/python
        Installing setuptools, pip, wheel...done.
        
        $ source venv/bin/activate

- Install/upgrade remark-compose:

        $ pip install --upgrade  https://github.com/igordejanovic/remark-compose/archive/master.zip


## Usage

Write `myconf.rconf` file. Rconf is a simple DSL for the generator
configuration consisting of global generator parameters and a set of rules.

      template = "path/to/template.html"

      "input/firstfile.md"
        title = "Title for the first slide deck"

      "input/secondfile.md" => "output/second_file_with_custom_out_name.html"
        title = "Title for the second slide deck"
        subtitle = "Subtitle for second slide deck"

        // Override template for this rule
        template = "path/to/other_template.html"

      "input2/*.md" => "output/"
        custom_param = "Some value"

Each `.rconf` rule defines input file
(or [glob2 pattern](https://github.com/miracle2k/python-glob2/)) and optionally
output file after `=>`. If output file is not given it will default to the same
directory and the same base name but using `.html` extension. Output can be
directory in which case full output name is created by adding the base name of
the input and `.html` extension.

Each rule may contain arbitrary number of additional parameters. Rule
parameters will override global parameters. `template` parameter is used to
define Jinja2 template which shall be used for output file generation. Usually
we have the same template for all rules and we shall define it globally.

All parameters, either rule level or global level are passed to the template
context so you can reference them from the template. E.g. in the previous
example we use it for `title` and `custom_param`. 

The content of input `.md` files will be rendered at the place of `{{content}}`
tag inside HTML template. 

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


To start a live server with auto-rebuild:

    $ remarkc serve myconf


For help:

    $ remarkc --help


or:

    $ remarkc serve --help


## Examples

- `Technology set` of slides (in Serbian language):
  - [rconf file for the set](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/tech.rconf)
  - [template.html for the set](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/template.html)
  - [base slides markdown template](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/base_slides.md)
  - [Python slides](http://igordejanovic.net/courses/tech/Python.html) -
    [source](https://raw.githubusercontent.com/igordejanovic/igordejanovic.github.io/master/courses/tech/Python.md),
    [generated](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/tech/Python.html)
  - [Git slides](http://igordejanovic.net/courses/tech/git.html) -
    [source](https://raw.githubusercontent.com/igordejanovic/igordejanovic.github.io/master/courses/tech/git.md),
    [generated](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/tech/git.html)
  - [Django slides](http://igordejanovic.net/courses/tech/django.html) -
    [source](https://raw.githubusercontent.com/igordejanovic/igordejanovic.github.io/master/courses/tech/django.md),
    [generated](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/tech/django.html)
  - [D3 slides](http://igordejanovic.net/courses/tech/d3.html) (an example
    using
    [template override](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/tech/template-d3.html)) -
    [source](https://raw.githubusercontent.com/igordejanovic/igordejanovic.github.io/master/courses/tech/d3.md),
    [generated](https://github.com/igordejanovic/igordejanovic.github.io/blob/master/courses/tech/d3.html)


## LICENSE

MIT

