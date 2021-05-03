# Final Project

Add any badges to your ***published documentation*** up here!

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Documenting your project](#documenting-your-project)
  - [Set up](#set-up)
  - [The writeup](#the-writeup)
    - [Requirements](#requirements)
  - [Build and publish](#build-and-publish)
    - [Read the Docs](#read-the-docs)
    - [GithubPages](#githubpages)
    - [Your own host](#your-own-host)
    - [Private options](#private-options)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Documenting your project

The main deliverable for your final project is the ***documentation*** you
provide here, in this repo, and where it is build.

We will be using [Sphinx](https://www.sphinx-doc.org/) to build static
documentation for your project, including any overview writeup, etc.

### Set up

Sphinx is trivial to set up.  You can use a cookiecutter template that includes
Sphinx, eg [cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage), or just follow the [quickstart](https://www.sphinx-doc.org/en/master/usage/quickstart.html).

### The writeup

Whether or not you actually add your main project code to this repository is up
to you.  Because we cannot assume you can deliver your code entirely to us (and
it would be hard for us to evaluate, anyways), you should treat the deliverable
here more like a paper than a code submission.

Please 'document' your project using Sphinx, a static site generator, to build
an HTML page that describes your project.

#### Requirements

Requirements are loose due to project flexibility, but as a guideline you should
include:

* An intro page to the problem

* An overview of your solution

* Ideally some diagram of the architecture

* Tangible snippets of python code in your discussion

* Some amount of [sphinx
autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html),
either from your 'real' code, or from toy snippets you include to describe
your approach, and some other sphinx cross references.

* A conclusion of the main learnings or contributions of your project

* Your Science Fair presentation should be similar to the content in the
writeup, but the writeup is your chance to go deeper into the topics and
really explain/demonstrate etc in more depth.

### Build and publish
It is easy to build sphinx documentation locally, but that is not good enough
for sharing.  You need to find a way to share your write up with us!  You have
a few options.

The biggest decision is whether you want your documentation and/or this repo
to be publicly viewable.

Note: you still need to 'submit' your assignment via CI/CD, just to ensure we
have the correct commit/tag of your repo, even if RTD/Github is doing most of
the build.  However, there is no explicit need for testing.

#### Read the Docs

It is very easy to publish sphinx docs on [Read the
Docs](https://readthedocs.org/)! The only caveat is that it requires your repo
to be public (that's fine from the teaching staff's point of view) and your docs
will be public too.  Go ahead and sign up, hook up your repo, and you are good
to go!

#### GithubPages

Github also can publish a webpage for you, based on sphinx in your repo.  The
Pages will be publicly viewable, but your repo can remain private.  Here is
[one example
walkthrough](https://www.docslikecode.com/articles/github-pages-python-sphinx/).

#### Your own host

Feel free to find another way to publish your docs!  We just require that it use
Sphinx and is automatically built from your master branch using CI/CD.

#### Private options

If you are not comfortable publishing your documentation publicly, you can still
build your sphinx project in CI/CD, zip up the build artifact, and upload that
to Canvas.  Your submission in this case will be the zipped html rather than the
link to this repo; ensure you still have the repo link in the submission
comments.
