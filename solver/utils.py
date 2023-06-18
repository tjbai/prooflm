import re

colors = {
    'BLACK': '\033[0;30m',
    'RED': '\033[0;31m',
    'GREEN': '\033[0;32m',
    'YELLOW': '\033[0;33m',
    'BLUE': '\033[0;34m',
    'MAGENTA': '\033[0;35m',
    'CYAN': '\033[0;36m',
    'WHITE': '\033[0;37m',
    'RESET': '\033[0m'
}

'''
Shamelessly stolen from https://github.com/JasonGross/coq-tools
'''

def merge_quotations(statements, sp=' '):
    """If there are an odd number of "s in a statement, assume that we
    broke the middle of a string.  We recombine that string."""
    cur = None 
    for i in statements:
        if i.count('"') % 2 != 0:
            if cur is None:
                cur = i 
            else:
                yield (cur + sp + i)
                cur = None 
        elif cur is None:
            yield i 
        else:
            cur += sp + i 

def strip_comments(contents):
    """Strips the comments from coq code in contents.

    The strings in contents are only preserved if there are no
    comment-like tokens inside of strings.  Stripping should be
    successful and correct, regardless of whether or not there are
    comment-like tokens in strings.

    The behavior of this method is undefined if there are any
    notations which change the meaning of '(*', '*)', or '"'.

    Note that we take some extra care to leave *) untouched when it
    does not terminate a comment.
    """
    contents = contents.replace('(*', ' (* ').replace('*)', ' *) ')
    tokens = contents.split(' ')
    rtn = []
    is_string = False
    comment_level = 0
    for token in tokens:
        do_append = (comment_level == 0)
        if is_string:
            if token.count('"') % 2 == 1: # there are an odd number of '"' characters, indicating that we've ended the string
                is_string = False
        elif token.count('"') % 2 == 1: # there are an odd number of '"' characters, so we're starting a string
            is_string = True
        elif token == '(*':
            comment_level += 1
            do_append = False
        elif comment_level > 0 and token == '*)':
            comment_level -= 1
        if do_append:
            rtn.append(token)
    return ' '.join(rtn).replace(' (* ', '(*').replace(' *) ', '*)').strip('\n\t ')

def split_coq_file_contents(contents):
    """Splits the contents of a coq file into multiple statements.

    This is done by finding one or three periods followed by
    whitespace.  This is a dumb algorithm, but it seems to be (nearly)
    the one that ProofGeneral and CoqIDE use.

    We additionally merge lines inside of quotations."""
    return list(merge_quotations(re.split('(?<=[^\.]\.\.\.)\s|(?<=[^\.]\.)\s', strip_comments(contents))))
