#!/usr/bin/env python3

def bin_search(S, g):
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        was_censored = yield (g[:mid],) + S
        if was_censored:
            hi = mid
        else:
            lo = mid
    return hi

def bisect_left(S, g, after):
    lo, hi = 0, len(g)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        was_censored = yield (g[mid:] + after,) + S
        if not was_censored:
            hi = mid
        else:
            lo = mid
    return lo

def comp_aware_bin_split(s):
    C = ()
    j = len(s)
    while True:
        i = yield from bin_search(C, s)
        j = min(i - 1, j - 1)
        while j > 0:
            was_censored = yield (s[:i-1], s[j:i]) + C
            if was_censored:
                break
            else:
                j = j - 1
        C = (s[j:i],) + C
        if j > 0:
            s = s[:i-1]
        else:
            s = ""
        if not s:
            break
        was_censored = yield C
        if was_censored:
            break
    return C

def comp_aware_bin_split_2(s):
    C = ()
    j = len(s)
    while True:
        i = yield from bin_search(C, s)
        diff = 1
        j = min(i - 1, j - 1)
        while j > 0:
            was_censored = yield (s[:i-1], s[j:i]) + C
            if was_censored:
                break
            else:
                j -= diff
                diff *= 2
        diff //= 2
        s_1 = s[:i]
        k = max(j, 0)
        j = yield from bisect_left((s_1[:-1],) + C,
                                   s_1[k:j+diff],
                                   s_1[j+diff:])
        j += k
        C = (s[j:i],) + C
        if j > 0:
            s = s[:i-1]
        else:
            s = ""
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
