# Contributing

This document describes how to contribute to this repository. Pull
requests containing bug fixes, updates, and extensions to the existing
tools and tool suites in this repository will be considered for
inclusion.

## What not to contribute

* New tools.

  If one wishes to add new tools to the Galaxy tool shed - it is
  probably best to at least start by publishing them under a personal
  or organizational account. If the tools are of sufficient quality and
  broad appeal - it may be worth discussing inclusion of them in the
  [Galaxy IUC repository][iuc] and that can be but this repository is
  mostly for older, existing tools pre-dating the IUC.

  There are nonetheless many existing tools here for very popular
  bioinformatics programs - extensions or bug fixes for these tools
  will certainly be considered.

* Purely stylistic fixes.

  This repository contains many old wrappers that are likely
  infrequently if ever used. If you are not actively planning on
  extending a tool and have not encountered a bug - it is probably
  best to just leave the tool alone so we can focus on newer more
  contemporarily useful tools.

  If you are looking for a good way to contribute to Galaxy - consider
  the ideas in [this Trello card](https://trello.com/c/eFdPIdIB).

## How to Contribute

* Make sure you have a [GitHub account](https://github.com/signup/free)
* Make sure you have git [installed](https://help.github.com/articles/set-up-git)
* Fork the repository on [GitHub](https://github.com/galaxyproject/tools-devteam/fork)
* This repository was derived from mercurial repositories in the tool
  shed and may contain certain artifacts that should be fixed before
  committing new functionality in such files. These include:

  * The tool shed will automatically assign certain fields in
    tool_dependencies.xml during upload - these fields should be left
    blank in this git repository. 

  * Related tools may be broken out into individual folders with
    duplicated wrapper scripts or macro files - these should be moved
    to a common location in this repository and symolically linked to
    the original locations prior to modification.
* Make the desired modifications - consider using a [feature branch](https://github.com/Kunena/Kunena-Forum/wiki/Create-a-new-branch-with-git-and-manage-branches).
* Make sure you have added the necessary tests for your changes and they pass.
* Open a [pull request](https://help.github.com/articles/using-pull-requests)
  with these changes.


[iuc]: https://github.com/galaxy-iuc/tool_shed
