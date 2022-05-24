#!/usr/bin/env python3

from simulator import Simulator

def bin_search(S, g):
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        was_censored = yield S.union({g[mid:]})
        if was_censored:
            lo = mid
        else:
            hi = mid
    return lo

def bisect_right(S, g, before):
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi + 1) // 2
        was_censored = yield S.union({before + g[:mid]})
        if not was_censored:
            lo = mid
        else:
            hi = mid
    return lo

def comp_aware_bin_split(s):
    C = set()
    while True:
        i = yield from bin_search(C, s)
        j = i + 1
        k = len(s)
        while j < k:
            was_censored = yield C.union({s[i:j], s[i+1:]})
            if was_censored:
                k = j
            else:
                j = j + 1
        C = C.union({s[i:j]})
        if j != len(s):
            s = s[i+1:]
        else:
            s = ''
        if not s:
            break
        was_censored = yield C
        if was_censored:
            break
    return C

def comp_aware_bin_split_2(s,):
    C = set()
    while True:
        i = yield from bin_search(C, s)
        diff = 1
        j = i + 1
        k = len(s)
        while j < k:
            was_censored = yield C.union({s[i:j], s[i+1:]})
            if was_censored:
                break
            else:
                j += diff
                diff *= 2
        diff //= 2
        s_1, j = s[i:], j - i
        j = yield from bisect_right(C.union({s_1[1:]}),
                                    s_1[j-diff:j],
                                    s_1[:j-diff])
        j += i + 1
        C = C.union({s[i:j+diff]})
        s = s[i+1:]
        if not s:
            break
        was_censored = yield C
        if was_censored:
            break
    return C

def isolate(isolator, sim):
    was_censored = None
    while True:
        try:
            test = isolator.send(was_censored)
        except StopIteration as e:
            return e.value
        was_censored = is_censored(test, sim)

def is_censored(test, sim):
    separator = '\x00' # will be platform specific
    return sim.send(separator.join(test))

def main():
    sim = Simulator()
    for art in sim.get_articles():
        isolator = comp_aware_bin_split_2(art)
        kw = isolate(isolator, sim)
        sim.report_found_keyword(kw)
        print(sim.query_log[sim.this_article])
    print(sim.queries / len(sim.articles))

if __name__ == "__main__":
    main()
