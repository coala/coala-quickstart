LOGO_STRING = """
  .o88Oo._
 d8P         .ooOO8bo._
 88                  '*Y8bo.
 YA                      '*Y8b   __
  YA                        68o68**8Oo.
   "8D                       *"'    "Y8o
    Y8     'YB                       .8D
    '8               d8'             8D
     8       d8888b          d      AY
     Y,     d888888         d'  _.oP"
      q.    Y8888P'        d8
       "q.  `Y88P'       d8"
          Y           ,o8P
               oooo888P"
"""
COALA_BEAR_LOGO = LOGO_STRING.split('\n')

WELCOME_MESSAGES = ['Hi there! Awesome you decided to do some high '
                    'quality coding. coala is just the tool you need!',

                    'You can configure coala to suit your needs. This '
                    'is done with a settings file called a `.coafile` '
                    'in the project directory.',

                    "We can help you with that. Let's get started with "
                    'some basic questions.']


GLOB_HELP_URL = 'http://coala.readthedocs.io/en/latest/Users/Glob_Patterns.html'
GLOB_HELP = """
File globs are a very concise way to specify a large
number of files. You may give multiple file globs
separated by commas. To learn more about glob patterns
please visit: {}

For example, you may want to include your src/ folder and
all its contents but exclude your .git directory and all
.o files. To do this, simply give `src/` for the first
question and `.git/**,**/*.o` for the second question.
""".format(GLOB_HELP_URL)

BEAR_DOCS_URL = ('https://github.com/coala/bear-docs/blob/master/'
                 'README.rst#supported-languages')
BEAR_HELP = """
A coala bear is a plugin that contains the checking routines. It may be
language specific or language independent. This makes coala completely
modularized and extensible. Many languages including C/C++, Python,
JavaScript are supported out-of-the-box.

You can see all of them here: {}
""".format(BEAR_DOCS_URL)
