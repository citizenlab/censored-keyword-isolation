#!/usr/bin/env python3

def bin_search(S, g, is_censored):
    """Perform a binary search over g and return the index of the leftmost
    character of the leftmost component of the keyword combination whose
    leftmost component is rightmost in g.
    :param S: tuple of strings to include with test messages
    :param g: str
    :return: index of the leftmost character of the leftmost component of the
    keyword combination whose leftmost component is rightmost in g
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if is_censored(S + (g[mid:],)):
            lo = mid
        else:
            hi = mid
    return lo

def bisect_right(S, g, before, is_censored):
    """Perform a binary search over g and return the index of the rightmost
    character of the rightmost component of the keyword combination whose
    rightmost component is leftmost in g.
    :param S: tuple of strings to include with test messages
    :param g: str
    :param before: prepend 'before' to tested slices of g
    :return: index of the rightmost character of the rightmost component of the
    keyword combination whose rightmost component is leftmost in g
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if not is_censored(S + (before + g[:mid],)):
            lo = mid
        else:
            hi = mid
    return lo

def comp_aware_bin_split(s, is_censored):
    """Isolates a censored keyword combination.  If more than one censored
    keyword combination is present, it isolate the one whose leftmost component
    is rightmost in g.
    :return: censored keyword combination
    """
    C = ()
    j = 0
    while True:
        i = bin_search(C, s, is_censored)
        j = max(i + 1, j)
        k = len(s)
        while j < k:
            if is_censored(C + (s[i:j], s[i+1:])):
                k = j
            else:
                j = j + 1
        C = C + (s[i:j],)
        if j != len(s):
            s = s[i+1:]
        else:
            s = ""
        if not s or is_censored(C):
            break
        j -= i
    return C

def comp_aware_bin_split_2(s, is_censored):
    """Modified version of comp_aware_bin_split which uses a binary search
    rather than linear search to identify ends of components.
    """
    C = ()
    j = 0
    while True:
        i = bin_search(C, s, is_censored)
        diff = 1
        j = max(i + 1, j)
        k = len(s)
        while j < k:
            if is_censored(C + (s[i:j], s[i+1:])):
                break
            else:
                j += diff
                diff *= 2
        diff //= 2
        s_1, j = s[i:], j - i
        j = i + 1 + bisect_right(C + (s_1[1:],),
                                 s_1[j-diff:j],
                                 s_1[:j-diff],
                                 is_censored)
        C = C + (s[i:j+diff],)
        if j + diff != len(s):
            s = s[i+1:]
        else:
            s = ""
        if not s or is_censored(C):
            break
        j -= i
    return C

def main():
    from simulator import Simulator
    sim = Simulator()
    def is_censored(test):
        separator = '\x00' # will be platform specific
        return sim.send(separator.join(test))
    for art in sim.get_articles():
        kw = comp_aware_bin_split(art, is_censored)
        sim.report_found_keyword(kw)
        print(sim.query_log[sim.this_article])
    print(sim.queries / len(sim.articles))

if __name__ == "__main__":
    main()
