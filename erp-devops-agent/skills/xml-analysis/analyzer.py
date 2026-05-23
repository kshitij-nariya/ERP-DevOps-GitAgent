from __future__ import annotations

from lxml import etree


def parse_xml(source: str):
    parser = etree.XMLParser(recover=False, huge_tree=False)
    return etree.fromstring(source.encode("utf-8"), parser=parser)
