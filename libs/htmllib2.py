import cgi
from htmlentitydefs import name2codepoint
import re

def escape(text):
	return cgi.escape(text, quote=True)

def unescape(text):
	return re.sub(u'&(%s);' % u'|'.join(name2codepoint), lambda mat: unichr(name2codepoint[mat.group(1)]), text)
