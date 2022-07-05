#!/usr/bin/env python3

def bin_search(S, g):
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        was_censored = yield S + (g[mid:],)
        if was_censored:
            lo = mid
        else:
            hi = mid
    return lo

def bisect_right(S, g, before):
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi + 1) // 2
        was_censored = yield S + (before + g[:mid],)
        if not was_censored:
            lo = mid
        else:
            hi = mid
    return lo

def comp_aware_bin_split(s):
    C = ()
    j = 0
    while True:
        i = yield from bin_search(C, s)
        j = max(i + 1, j)
        k = len(s)
        while j < k:
            was_censored = yield C + (s[i:j], s[i+1:])
            if was_censored:
                k = j
            else:
                j = j + 1
        C = C + (s[i:j],)
        if j != len(s):
            s = s[i+1:]
        else:
            s = ''
        if not s:
            break
        was_censored = yield C
        if was_censored:
            break
        j -= i
    return C

def comp_aware_bin_split_2(s,):
    C = ()
    j = 0
    while True:
        i = yield from bin_search(C, s)
        diff = 1
        j = max(i + 1, j)
        k = len(s)
        while j < k:
            was_censored = yield C + (s[i:j], s[i+1:])
            if was_censored:
                break
            else:
                j += diff
                diff *= 2
        diff //= 2
        s_1, j = s[i:], j - i
        j = yield from bisect_right(C + (s_1[1:],),
                                    s_1[j-diff:j],
                                    s_1[:j-diff])
        j += i + 1
        C = C + (s[i:j+diff],)
        if j + diff != len(s):
            s = s[i+1:]
        else:
            s = ""
        if not s:
            break
        was_censored = yield C
        if was_censored:
            break
        j -= i
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
    from simulator import Simulator
    sim = Simulator()
    for art in sim.get_articles():
        isolator = comp_aware_bin_split(art)
        kw = isolate(isolator, sim)
        sim.report_found_keyword(kw)
        print(sim.query_log[sim.this_article])
    print(sim.queries / len(sim.articles))

if __name__ == "__main__":
    main()
