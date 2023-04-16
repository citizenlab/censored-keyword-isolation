#!/usr/bin/env python3

def bin_search(S, g, is_censored):
    """Perform a binary search over g and return the index of the rightmost
    character of the rightmost component of the keyword combination whose
    rightmost component is leftmost in g.
    :param S: set of strings to include with test messages
    :param g: str
    :return: index of the rightmost character of the rightmost component of the
    keyword combination whose rightmost component is leftmost in g
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if is_censored({g[:mid]}.union(S)):
            hi = mid
        else:
            lo = mid
    return hi

def bisect_left(S, g, after, is_censored):
    """Perform a binary search over g and return the index of the leftmost
    character of the leftmost component of the keyword combination whose
    leftmost component is rightmost in g.
    :param S: set of strings to include with test messages
    :param g: str
    :param before: append 'after' to tested slices of g
    :return: index of the leftmost character of the leftmost component of the
    keyword combination whose leftmost component is rightmost in g
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if not is_censored({g[mid:] + after}.union(S)):
            hi = mid
        else:
            lo = mid
    return lo

def comp_aware_bin_split(s, is_censored):
    """Isolates a censored keyword combination.  If more than one censored
    keyword combination is present, it isolate the one whose rightmost
    component is leftmost in g.
    :return: censored keyword combination
    """
    C = set()
    j = len(s)
    while True:
        i = bin_search(C, s, is_censored)
        j = min(i - 1, j - 1)
        while j > 0:
            if is_censored({s[:i-1], s[j:i]}.union(C)):
                break
            else:
                j = j - 1
        C = {s[j:i]}.union(C)
        if j > 0:
            s = s[:i-1]
        else:
            s = ""
        if not s or is_censored(C):
            break
    return C

def comp_aware_bin_split_2(s, is_censored):
    """Modified version of comp_aware_bin_split which uses a binary search
    rather than linear search to identify ends of components.
    """
    C = set()
    j = len(s)
    while True:
        i = bin_search(C, s, is_censored)
        diff = 1
        j = min(i - 1, j - 1)
        while j > 0:
            if is_censored({s[:i-1], s[j:i]}.union(C)):
                break
            else:
                j -= diff
                diff *= 2
        diff //= 2
        s_1 = s[:i]
        k = max(j, 0)
        j = k + bisect_left({s_1[:-1]}.union(C),
                            s_1[k:j+diff],
                            s_1[j+diff:],
                            is_censored)
        C = {s[j:i]}.union(C)
        if j > 0:
            s = s[:i-1]
        else:
            s = ""
        if not s or is_censored(C):
            break
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
