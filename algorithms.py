#!/usr/bin/env python3

import math
from simulator import Simulator

NULL_CHAR = '\x00'


def is_censored(msg):
    """Test a string or list of strings for censorship.
    :return: True if msg was censored, False otherwise
    """
    if isinstance(msg, str):
        return sim.send(msg)
    return sim.send(NULL_CHAR.join(msg))


def bin_search(S, g):
    """Perform a binary search over g and return the index of the first
    sensitive component in g.
    :param S: set of strings to include with test messages
    :param g: str
    :return: index of first sensitive character in g
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = math.floor((lo+hi) / 2)
        if is_censored(S.union({g[mid:]})):
            lo = mid
        else:
            hi = mid
    return lo


def bin_search_right(S, g):
    """Perform a binary search over g and return the index of the rightmost
    censored character instead of the leftmost.
    """
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if not is_censored(S.union({g[:mid]})):
            lo = mid
        else:
            hi = mid
    return lo


def bisect_right(S, g, before):
    """Similar to bin_search_right, but prepend 'before' to tested slice"""
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi + 1) // 2
        if not is_censored(S.union({before + g[:mid]})):
            lo = mid
        else:
            hi = mid
    return lo


def split_comps(C):
    """Given a set of strings C, identify any additional splits that can be
    made to isolate keyword components and return the exact sensitive keyword
    combination.
    """
    D = set()
    for s in C:
        i = 0
        for j in range(1, len(s)):
            if is_censored(set(C).difference({s}).union({s[:j], s[j:]})):
                D = D.union({s[i:j]})
                i = j
        if i < len(s):
            D = D.union({s[i:]})
    return D


def split_comps_2(C):
    """Improved version of split_comps which is slightly more efficient and
    correctly identifies overlapping components.
    """
    for s in list(C):
        C.remove(s)
        while len(s) > 1 and is_censored(C.union({s[1:], s[:-1]})):
            C.add(s[:1 + bin_search_right(C.union({s[1:]}), s[:-1])])
            s = s[1 + bin_search(C, s[1:]):]
        C.add(s)
    return C


def bin_search_w_backtracking(s):
    """Extends binary search to find complete sensitive subsequences of
    characters, by trialing partial text removals until only sensitive
    characters remain.
    :return: sensitive keyword combination as a set of strings
    """
    stack = [(0, len(s))]
    while stack:
        lo, hi = stack.pop()
        s_1 = s[:lo] + NULL_CHAR * (hi - lo) + s[hi:]
        if hi - lo < len(s) and is_censored(s_1):
            s = s_1
        elif hi - lo > 1:
            mid = (lo + hi) // 2
            stack.append((mid, hi))
            stack.append((lo, mid))
    C = {seg for seg in s.split(NULL_CHAR) if seg}
    return split_comps(C)


def bin_split(s):
    """Use bin_search iteratively to identify a sensitive keyword combination.
    :return: sensitive keyword combination as a set of strings
    """
    C = set()
    t = ""
    while True:
        i = bin_search(C.union({t}), s)
        if i != 0 and t:
            C = C.union({t})
            t = ""
        t = t + s[i]
        s = s[i+1:]
        if len(s) == 0 or is_censored(C.union({t})):
            break
    if t:
        C = C.union({t})
    return split_comps(C)


def comp_aware_bin_split(s):
    """Improved version of bin_split adapted to for identifying keyword combos
    :return: sensitive keyword combination as a set of strings
    """
    C = set()
    while True:
        i = bin_search(C, s)
        j = i + 1
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
    return C


def comp_aware_bin_split_2(s):
    """Modified version of comp_aware_bin_split which uses a binary search
    rather than linear search to identify ends of components.
    """
    C = set()
    while True:
        i = bin_search(C, s)
        diff = 1
        j = i + 1
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
                                 s_1[:j-diff])
        C = C.union({s[i:j+diff]})
        s = s[i+1:]
        if not s or is_censored(C):
            break
    return C


if __name__ == "__main__":
    sim = Simulator()
    for art in sim.get_articles():
        kw = comp_aware_bin_split(art)
        sim.report_found_keyword(kw)
        print(sim.query_log[sim.this_article])
    print(sim.queries / len(sim.articles))
