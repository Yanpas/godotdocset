#!/usr/bin/python3
# coding: utf-8

'''
MIT license, author Yan Pas
'''

import jinja2
import xml.etree.ElementTree as etree
import argparse
from types import SimpleNamespace
import os
import os.path
import sys
import re
from glob import glob

def linkify_text(txt):
	return re.sub(r'\[(.+?)\]', r'<a href="\1.html">\1</a>', txt)

def j_print_args(args, **_kwargs):
	return ", ".join(['<a href="{0}.html">{0}</a> {1}{dflt}'.format(a.type, a.name, dflt=("="+a.default if a.default else "")) for a in args])

class DocPage:
	parents = {}

	def __init__(self, root: etree.Element):
		self._root = root
		self.title = root.attrib["name"]
		self.inherits = root.attrib.get("inherits")
		self.parents = []
		DocPage.parents[self.title] = self.inherits
		self.category = root.attrib["category"]
		self.brief_description = linkify_text(root.find('brief_description').text.strip())
		self.description = linkify_text(root.find('description').text.strip())
		self.populate_methods()
		self._j_print_args = j_print_args
		self.populate_signals()
		self.populate_fields()
		self.populate_consts()

		del self._root

	def build_parents(self):
		name = self.title
		if name not in DocPage.parents:
			print("Failed to find parent %s for %s" % (name, self.title), file=sys.stderr)
			return
		while DocPage.parents[name]:
			name = DocPage.parents[name]
			self.parents.append(name)
			if name not in DocPage.parents:
				print("Failed to find parent %s for %s" % (name, self.title), file=sys.stderr)
				break

	def populate_methods(self):
		self.methods = []
		cnt = 1
		for method in self._root.findall("methods/method"):
			res = SimpleNamespace()
			res.cnt = cnt
			res.name = method.attrib["name"]
			res.__dict__["return"] = method.find("return").attrib["type"] if method.find("return") else "void"
			res.description = method.find("description").text.strip()
			res.arguments = []
			for arg in method.findall("argument"):
				res.arguments.append(SimpleNamespace(index=int(arg.attrib["index"]), name=arg.attrib["name"],
						type=arg.attrib["type"], default=(arg.attrib.get('default'))))
			res.arguments.sort(key=lambda el: el.index)
			self.methods.append(res)
			cnt += 1

	def populate_signals(self):
		self.signals = []
		for sig in self._root.findall("signals/signal"):
			res = SimpleNamespace()
			res.name = sig.attrib['name']
			res.description = sig.find("description").text.strip()
			res.arguments = []
			for arg in sig.findall("argument"):
				res.arguments.append(SimpleNamespace(index=int(arg.attrib["index"]), name=arg.attrib["name"],
						type=arg.attrib["type"], default=(arg.attrib.get('default'))))
			res.arguments.sort(key=lambda el: el.index)
			self.signals.append(res)
		
	def populate_fields(self):
		self.fields = []
		for field in self._root.findall("members/member"):
			res = SimpleNamespace()
			res.name = field.attrib['name']
			res.description = field.text.strip()
			res.type = field.attrib['type']
			self.fields.append(res)

	def populate_consts(self):
		self.consts = {}
		for const in self._root.findall("constants/constant"):
			ename = const.attrib.get("enum")
			if ename not in self.consts:
				self.consts[ename] = []
			res = SimpleNamespace(name=const.attrib['name'], value=const.attrib['value'])
			res.description = linkify_text(const.text.strip())
			self.consts[ename].append(res)

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument('-f', '--from', help="folder or xml file", required=True)
	ap.add_argument('-t', '--to', help="output folder", default='.')
	args = ap.parse_args()
	frompath = args.__dict__['from']
	def dump(content, name):
		with open(os.path.join(args.to, name[:-4] + ".html"), 'w', encoding="utf-8") as f:
			f.write(content)
	
	tpl = jinja2.Template(open('template.jinja2').read())
	if not os.path.exists(frompath):
		exit("File or directory " + frompath + " doesn't exist")
	elif os.path.isfile(frompath):
		doc = etree.parse(frompath)
		dp = DocPage(doc.getroot())
		render = tpl.render(vars(dp))
		dump(render, os.path.basename(frompath))
	else:
		if not os.path.exists(args.to):
			os.mkdir(args.to)
		docpages = {}
		for fname in glob(frompath + "/*.xml"):
			doc = etree.parse(fname)
			print("parsing", fname)
			docpages[fname] = DocPage(doc.getroot())
		for fname, dp in docpages.items():
			dp.build_parents()
			render = tpl.render(vars(dp))
			dump(render, os.path.basename(fname))
