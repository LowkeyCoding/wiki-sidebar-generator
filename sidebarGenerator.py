from __future__ import annotations
import os
import argparse
from git.repo.base import Repo
from dataclasses import dataclass, field
from typing import List

parser = argparse.ArgumentParser(description="Generate custom collapsible sidebar")
parser.add_argument("--repo", action="store", dest="repo", required=True)
parser.add_argument("--out", action="store", dest="out", default="_Sidebar.md")
parser.add_argument("--wiki", action="store", dest="wiki", default="./wiki")
args = parser.parse_args()
WIKI_DIR = args.wiki
REPO = args.repo
OUTPUT_DIR = WIKI_DIR + "/" + args.out


def get_headers(markdown):
    res = []
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("#"):
            res.append(line)
    return res


def to_file(string, filename):
    f = open(filename, "a")
    f.write(string)
    f.close()


def main():
    linkPrefix = REPO + "/wiki/"
    if not os.path.exists(WIKI_DIR):
        Repo.clone_from(REPO + ".wiki.git", WIKI_DIR)
    if os.path.exists(OUTPUT_DIR):
        f = open(OUTPUT_DIR, "w")
        f.close()
    dirs = os.listdir(WIKI_DIR)
    dirs.sort()
    for file in dirs:
        if file.endswith(".md") and not file.startswith("_"):
            name = file[:-3]
            f = open(WIKI_DIR + "/" + file, "r")
            headers = get_headers(f.read())
            parser = Parser(headers, name)
            parser.parse()
            generate = MarkdownGenerator(parser.HeadEntry, linkPrefix)
            generate.generate()
            to_file(generate.Markdown, OUTPUT_DIR)
    print("Finished generating sidebar")


@dataclass
class Entry:
    Title: str = "undefined"
    Level: int = 0
    Parent: Entry = None
    Children: list[Entry] = field(default_factory=list)


class MarkdownGenerator:
    Markdown: str
    LinkPrefix: str
    HeadEntry: str
    EntryNamesDict: dict(str, int)
    LinkName: str

    def __init__(self, headEntry: Entry, linkPrefix: str):
        self.HeadEntry = headEntry
        self.LinkPrefix = linkPrefix
        self.Markdown = ""
        self.LinkName = headEntry.Title
        self.EntryNamesDict = {}

    def generate(self):
        self.Markdown = ""
        self.entries_to_markdown(self.HeadEntry, 0, 8)

    def print_entries(self, entry):
        self.print_entry(entry)
        for _entry in entry.Children:
            self.print_entries(_entry)

    def print_entry(self, entry: Entry):
        print(f'{" " * entry.Level}{entry.Title} - {entry.Level}')

    def entries_to_markdown(self, entry: Entry, level: int, indent: int):
        indentStr = " " * (level * indent)
        if entry.Parent != None and entry.Parent.Title == self.HeadEntry.Title:
            self.LinkName = entry.Title

        if len(entry.Children) > 0:
            level2 = level + 1
            self.Markdown += f"{indentStr}<details>\n"
            self.entry_to_markdown(entry, level, indent)
            self.Markdown += f'{indentStr +(" " * indent)}<blockqoute>\n'
            for child in entry.Children:
                self.entries_to_markdown(child, level + 1, indent)
            self.Markdown += f'{indentStr +(" " * indent)}</blockqoute>\n'
            self.Markdown += f"{indentStr}</details>"
        else:
            self.entry_to_markdown(entry, level, indent)

    def entry_to_markdown(self, entry: Entry, level: int, indent: int):
        self.Markdown += f'{" " * (level * indent)}<summary><a href="{self.LinkPrefix}/{self.get_link_name(entry)}">{entry.Title}</a></summary>\n'

    def get_link_name(self, entry: Entry):
        name = ""
        if self.HeadEntry.Title == entry.Title:
            name = entry.Title
        elif entry.Title in self.EntryNamesDict:
            name = f"{self.HeadEntry.Title}{'#'}{entry.Title}-{self.EntryNamesDict[entry.Title]}"
            self.EntryNamesDict[entry.Title] += 1
        else:
            name = f"{self.HeadEntry.Title}{'#'}{entry.Title}"
            self.EntryNamesDict[entry.Title] = 1
        return name


class Parser:
    Headers: list[str]
    HeadEntry: Entry

    def __init__(self, headers: List[str], name: str):
        self.Headers = headers
        self.HeadEntry = Entry(Title=name)

    def parse(self):
        last_entry = self.HeadEntry
        for header in self.Headers:
            entry = Entry(self.get_title(header), self.get_level(header), last_entry)
            if entry.Level == last_entry.Level:
                entry.Parent = last_entry.Parent
                entry.Parent.Children.append(entry)
            elif entry.Level > last_entry.Level:
                entry.Parent = last_entry
                entry.Parent.Children.append(entry)
            else:
                parent = self.get_parent(entry, last_entry)
                entry.Parent = parent
                entry.Parent.Children.append(entry)
            last_entry = entry
        self.print_entries(self.HeadEntry)

    def get_parent(self, entry: Entry, last_entry: Entry):
        parent = last_entry.Parent
        while parent.Level >= entry.Level and parent.Parent != None:
            parent = parent.Parent
        return parent

    def print_entries(self, entry):
        self.print_entry(entry)
        for _entry in entry.Children:
            self.print_entries(_entry)

    def print_entry(self, entry: Entry):
        print(f'{" " * entry.Level}{entry.Title} - {entry.Level}')

    def get_level(self, header: str):
        level = 0
        for char in header:
            if char == "#":
                level += 1
            else:
                break
        return level

    def get_title(self, header: str):
        res = header.split(" ", 1)
        if len(res) > 1:
            return res[1]
        return "undefined"


main()
