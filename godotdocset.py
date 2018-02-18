#!/usr/bin/python3
# coding: utf-8

'''
MIT license, author Yan Pas
'''

import jinja2
# import xmlschema
import xml.etree.ElementTree as etree
import argparse
from types import SimpleNamespace
import os
import os.path

def j_print_method(method, **kwargs):
	args = ['<a href="{0}.html">{0}</a> {1}'.format(a.type, a.name) for a in method.arguments]
	return '<a href="#m_{name}" class="method_link">{name}</a> ({args})'.format(args=', '.join(args), **vars(method)) 

class DocPage:
	def __init__(self, root: etree.Element):
		self._root = root
		self.title = root.attrib["name"]
		self.inherits = [root.attrib["inherits"]]
		self.category = root.attrib["category"]
		self.brief_description = root.find('brief_description').text.strip()
		self.populate_methods()
		self._j_print_method = j_print_method
		self.populate_signals()

		del self._root

	def populate_methods(self):
		self.methods = []
		for method in self._root.findall("methods/method"):
			res = SimpleNamespace()
			res.name = method.attrib["name"]
			res.__dict__["return"] = method.find("return").attrib["type"]
			res.description = method.find("description").text.strip()
			res.arguments = []
			for arg in method.findall("argument"):
				res.arguments.append(SimpleNamespace(index=int(arg.attrib["index"]), name=arg.attrib["name"],
						type=arg.attrib["type"]))
			res.arguments.sort(key=lambda el: el.index)
			self.methods.append(res)

	def populate_signals(self):
		self.signals = []
		for sig in self._root.findall("signals/signal"):
			res = SimpleNamespace()
			res.name = sig.attrib['name']
			res.description = sig.find("description").text.strip()
			res.arguments = []
			for arg in sig.findall("argument"):
				res.arguments.append(SimpleNamespace(index=int(arg.attrib["index"]), name=arg.attrib["name"],
						type=arg.attrib["type"]))
			res.arguments.sort(key=lambda el: el.index)
			self.methods.append(res)


fname = "classes/Animation.xml"

if __name__ == '__main__':
	# xs = xmlschema.XMLSchema('schema.xsd')
	# doc = xs.to_dict("classes/Animation.xml")
	doc = etree.parse(fname)

	tpl = jinja2.Template(open('template.jinja2').read())
	dp = DocPage(doc.getroot())

	render = tpl.render(vars(dp))
	# print(render)
	with open(os.path.basename(fname) + ".html", 'w') as f:
		f.write(render)