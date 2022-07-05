#!/usr/bin/env python3

def bin_search(S, g, is_censored):
    """Perform a binary search over g and return the index of the first
    sensitive component in g.
    :param S: set of strings to include with test messages
    :param g: str
    :return: index of first sensitive character in g
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if is_censored(S.union({g[mid:]})):
            lo = mid
        else:
            hi = mid
    return lo

def bisect_right(S, g, before, is_censored):
    """Perform a binary search over g and return the index of the rightmost
    censored character instead of the leftmost, prepending 'before' to tested
    slice.
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi + 1) // 2
        if not is_censored(S.union({before + g[:mid]})):
            lo = mid
        else:
            hi = mid
    return lo

def comp_aware_bin_split(s, is_censored):
    """Improved version of bin_split adapted to for identifying keyword combos
    :return: sensitive keyword combination as a set of strings
    """
    C = set()
    j = 0
    while True:
        i = bin_search(C, s, is_censored)
        j = max(i + 1, j)
        k = len(s)
        while j < k:
            if is_censored(C.union({s[i:j], s[i+1:]})):
                k = j
            else:
                j = j + 1
        C = C.union({s[i:j]})
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
    C = set()
    j = 0
    while True:
        i = bin_search(C, s, is_censored)
        diff = 1
        j = max(i + 1, j)
        k = len(s)
        while j < k:
            if is_censored(C.union({s[i:j], s[i+1:]})):
                break
            else:
                j += diff
                diff *= 2
        diff //= 2
        s_1, j = s[i:], j - i
        j = i + 1 + bisect_right(C.union({s_1[1:]}),
                                 s_1[j-diff:j],
                                 s_1[:j-diff],
                                 is_censored)
        C = C.union({s[i:j+diff]})
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
