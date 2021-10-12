import os
import argparse
from git.repo.base import Repo

parser = argparse.ArgumentParser(description='Generate custom collapsible sidebar')
parser.add_argument('--repo', action="store", dest="repo", required=True)
parser.add_argument('--out', action="store", dest="out", default="_Sidebar.md")
parser.add_argument('--wiki', action="store", dest="wiki", required=True)
args = parser.parse_args()
OUTPUT_DIR = args.out
WIKI_DIR = args.wiki
REPO = args.repo

def extraHeaders(markdown):
    res = []
    lines = markdown.split('\n')
    for line in lines:
        if line.startswith('#'): 
            res.append(line)
    return res

def main():
    linkPrefix = REPO+"/wiki/"
    if not os.path.exists(WIKI_DIR):
        Repo.clone_from(REPO+".wiki.git", WIKI_DIR)
    if os.path.exists(OUTPUT_DIR):
        f = open(OUTPUT_DIR, 'w')
        f.close()
    with os.scandir(WIKI_DIR) as it:
        for entry in it:
            if entry.name.endswith(".md") and not entry.name.startswith('_') and entry.is_file():
                name = entry.name[:-3]
                f = open(entry.path, 'r')
                headers = extraHeaders(f.read())
                menuGen = MenuGenerator(headers, name, linkPrefix)
                menuGen.gen(OUTPUT_DIR)
    print("Finished generating sidebar")

class MenuGenerator():
    def __init__(self, lines, name, prefix):
        menu = Menu()
        menu.Name = name
        menu.Link = prefix + name
        self.Lines = lines
        self.Index = 0
        self.Menu = menu
    def gen(self, filename):
        while(self.Index < len(self.Lines)):
            res = self.generateMenu(3)
            self.Menu.Nodes.append(res)
        self.toFile(filename)

    def generateMenu(self, level):
        line = self.Lines[self.Index].strip()
        menu = Menu()
        if(line.startswith('###')):
            menu.fill(line, 0, self.Menu)
            return menu
        elif(line.startswith('##')):
            menu.fill(line, 1, self.Menu)
        elif(line.startswith('#')):
            menu.fill(line, 2, self.Menu)
        
        if menu.Level >= level:
            return None
        running = True
        while(running and self.Index+1 < len(self.Lines)):
            self.Index+=1
             
            res = self.generateMenu(menu.Level)
            if not res == None:
                menu.Nodes.append(res)
            else:
                running = False
                self.Index-=1
        if(level == 2):
            self.Index -= 1
        self.Index += 1
        return menu
                
    def toFile(self, filename):
        f = open(filename, 'a')
        f.write(self.Menu.toMarkdown())
        f.close()
             
class Menu():
    
    def __init__(self):
        self.Name = ""
        self.Nodes = []
        self.Link = ""
        self.Level = 0
    def fill(self, line, level, top):
        self.Name = line[4-level:]
        self.Link = top.Link + "#" + self.Name
        self.Level = level
    
    def Print(self, indent):
        print("   " * indent, self.Name)
        for node in self.Nodes:
            node.Print(indent+1)
    
    def toMarkdown(self):
        res = ""
        if(len(self.Link) > 0):
            res += f"<details><summary> <a href=\"{self.Link}\">{self.Name}</a> </summary><blockquote>\n"
        else:
            res += f"<details><summary> ${self.Name} </summary><blockquote>\n"
        for node in self.Nodes:
            res += node.toMarkdown()
        res += "</blockquote></details>"
        return res


main()
