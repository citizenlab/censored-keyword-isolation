#!/usr/bin/env python3

# populate this list with articles to test
articles = [
    "委员会共同主席在报告发布记者会上表示：“这份报告是针对中国政府持续并广泛侵犯人权问题现"
    "况的一个全面诊断，包括各项领域。从宗教开始，在习近平主政下中国宗教自由每况愈下，特别"
    "是对宗教活动的镇压，即使是支持政府并获得政府所核准的宗教团体也不例外的成为镇压的目标"
    "。地下教会、法轮功、维吾尔族、藏传佛教、天主教、基督徒都面临了前所未有的镇压。",
    "對被控主持在新疆推行相關政策的中國官員實施制裁，包括名列中共政治局委員的新疆黨委書記陳"
    "全國。中央社報導指出，美中貿易戰正如火如荼進行，然而因北韓發展核武引發的僵局，美方若為"
    "了人權問題決定對中方採取制裁行動將是罕見做法，而對陳全國這樣的中國高官下手更將是前所未"
    "見，勢必令北京大怒。《紐約時報》10日則引述現任和前任美國官員的談話，指出川普政府官員正"
    "考慮制裁中國高級官員和公司，以懲罰中國把幾十萬維吾爾和其他少數民族穆斯林關進大型集中營"
    "的做法",
    "一帶來二二調整體三三三領域四四四四",
]

# populate this set with sensitive keyword combinations
keywords = {
    frozenset({"新疆", "集中營"}),
    frozenset({"法轮功"}),
    frozenset({"帶來", "調整", "整體", "領域"}),
}


class Simulator:
    """
    Locally simulate the behaviour of a chat app performing text censorship via
    sensitive keyword combinations, to assess the performance of keyword
    combination isolating algorithms.
    Usage:
        sim = Simulator() - inits and loads kws and articles
        this_art = sim.get_article() - get text of next article to test
        is_censored = sim.send(msg) - simulate whether message would be filtered
                                      based on kw list
        sim.report_found_keyword(proposed_kw) - report kw that algorithm found
        sim.kws_in_this_article() - return all keywords present in article
    """
    def __init__(self):
        self.articles = articles.copy()
        self.keywords = keywords.copy()
        self.this_article = -1
        self.queries = 0
        self.query_log = {}

        print("Simulator initialized with %d articles and %d keywords" %
              (len(self.articles), len(self.keywords)))

    def get_articles(self):
        """Return text of next article"""
        while self.this_article + 1 < len(self.articles):
            self.this_article += 1
            self.query_log[self.this_article] = 0
            yield self.articles[self.this_article]

    def send(self, msg):
        """Returns whether the message would have been censored based on the kws
        implemented.
        """
        self.queries += 1
        self.query_log[self.this_article] += 1
        is_censored = False
        for this_kw in self.keywords:
            if all(k in msg for k in this_kw):
                is_censored = True
                break
        return is_censored

    def report_found_keyword(self, proposed_kw):
        """Take a found keyword and return whether the keyword was correctly
        identified.
        """
        kws_in_this_article = self.kws_in_this_article()
        if set(proposed_kw) in kws_in_this_article:
            return True
        else:
            print('article index: %d' % self.this_article)
            print('found_combo: %s', proposed_kw)
            print('expected combo: %s', [tuple(sorted(combo)) for combo in kws_in_this_article])
            return False

    def kws_in_this_article(self):
        """Return keywords that are present in the current article
        :return: list of kws as frozenset
        """
        kws_in_art = []
        for this_kw in self.keywords:
            if all([k in self.articles[self.this_article] for k in this_kw]):
                kws_in_art.append(this_kw)
        return kws_in_art


if __name__ == '__main__':
    pass
