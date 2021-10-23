"""
Generate a file tree table of contents for a directory of markdown files

run from command line:

    $ python md_file_tree.py

will generate a  markdown index of all markdown files in the current working
directory and its sub folders and insert it into  a file `index.md`.
If a previous index exists in the file it will be replaced,
otherwise a new index will be created at the end of the file
or a new file created.

The index will be linked to the files
eg.
`  - [how_to_take_notes.md](./notetaking/how_to_take_notes.md)`
for a link to a file `how_to_take_notes.md` in the sub-folder `notetaking`

Options:
the filename can be explicitly specified
 $ python md_file_tree.py README.md

-f:  The headers in each file will be listed under the file link
-w:  Wikilink syntax `[[./notetaking/how_to_take_notes.md]]`
     will be used instead of common markdown

author: elfnor <elfnor.com>
"""
import re
import os
import argparse

TOC_LIST_PREFIX = "-"
HEADER_LINE_RE = re.compile("^(#+)\s*(.*?)\s*(#+$|$)", re.IGNORECASE)
HEADER1_UNDERLINE_RE = re.compile("^-+$")
HEADER2_UNDERLINE_RE = re.compile("^=+$")


def toggles_block_quote(line):
    """Returns true if line toggles block quotes on or off
    (i.e. finds odd number of ```)"""
    n_block_quote = line.count("```")
    return n_block_quote > 0 and line.count("```") % 2 != 0


def create_index(cwd):
    """create markdown index of all markdown files in cwd and sub folders"""
    base_len = len(cwd)
    base_level = cwd.count(os.sep)
    md_lines = []
    md_exts = [".pdf"]
    md_lines.append("<!-- filetree -->\n\n")
    for root, dirs, files in os.walk(cwd):
        files = sorted(
            [f for f in files if not f[0] == "." and os.path.splitext(f)[-1] in md_exts]
        )
        dirs[:] = sorted([d for d in dirs if not d[0] == "."])
        if len(files) > 0:
            level = root.count(os.sep) - base_level
            indent = "  " * level
            if root != cwd:
                indent = "  " * (level - 1)
                md_lines.append(
                    "{0} {2} **{1}/**\n".format(
                        indent, os.path.basename(root), TOC_LIST_PREFIX
                    )
                )
            rel_dir = ".{1}{0}".format(os.sep, root[base_len:])
            for md_filename in files:
                indent = "  " * level
                md_lines.append(
                    "{0} {3} [{1}]({2}{1})\n".format(
                        indent, md_filename, rel_dir, TOC_LIST_PREFIX
                    )
                )

    md_lines.append("\n<!-- filetreestop -->\n")
    return md_lines


def replace_index(filename, new_index):
    """finds the old index in filename and replaces it with the lines in new_index
    if no existing index places new index at end of file
    if file doesn't exist creates it and adds new index
    will only replace the first index block in file  (why would you have more?)
    """

    pre_index = []
    post_index = []
    pre = True
    post = False
    try:
        with open(filename, "r") as md_in:
            for line in md_in:
                if "<!-- filetree" in line:
                    pre = False
                if "<!-- filetreestop" in line:
                    post = True
                if pre:
                    pre_index.append(line)
                if post:
                    post_index.append(line)
    except FileNotFoundError:
        pass

    with open(filename, "w") as md_out:
        md_out.writelines(pre_index)
        md_out.writelines(new_index)
        md_out.writelines(post_index[1:])


def main():
    """generate index optional cmd line arguments"""
    parser = argparse.ArgumentParser(
        description=(
            "generate a markdown index tree of markdown files"
            "in current working directory and its sub folders"
        )
    )

    parser.add_argument(
        "filename", nargs="?", default="index.md", help="markdown output file"
    )

    args = parser.parse_args()

    cwd = os.getcwd()
    md_lines = create_index(cwd)

    md_out_fn = os.path.join(cwd, args.filename)
    replace_index(md_out_fn, md_lines)


if __name__ == "__main__":
    main()
