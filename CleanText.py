def replaceUnicode(string, replace=" "):
    return ''.join([(c if ord(c)<= 255 else replace) for c in string])
    
def unescapeHtml(html):
    newhtml = html
    newhtml = newhtml.replace("&lt;", "<")
    newhtml = newhtml.replace("&gt;", ">")
    newhtml = newhtml.replace("&quot;", "\"")
    newhtml = newhtml.replace("&apos;", "\'")
    newhtml = newhtml.replace("&amp;", "&")
    return newhtml