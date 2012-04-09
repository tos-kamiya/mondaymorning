#coding: utf-8

import unittest
import mondaymorning as mm


class Test(unittest.TestCase):
    def test_is_dot_file(self):
        self.assertFalse(mm.is_dot_file("f"))
        self.assertTrue(mm.is_dot_file(".f"))
        self.assertFalse(mm.is_dot_file("."))
        self.assertFalse(mm.is_dot_file(".."))

    def test_safe_stat_time(self):
        r = mm.safe_stat_time("*some non-existing file*")
        self.assertEqual(r, 0)

    def test_merge_paths_by_directory_structure(self):
        L = [(1, u"d/a"), (1, u"d/a/b"), (1, u"d/a/c")]
        r = mm.merge_paths_by_directory_structure(L)
        self.assertEqual(r, [(1, u"d/a"), (1, u"d/a/{b,c}")])

        L = [(1, u"d/a"), (2, u"d/a/b"), (3, u"d/a/c")]
        r = mm.merge_paths_by_directory_structure(L)
        self.assertEqual(r, [(1, u"d/a"), (2, u"d/a/b"), (3, u"d/a/c")])

    def test_normalize_url(self):
        url = u"""https://www.google.co.jp/#hl=ja&sugexp=frgbld&gs_nf=1&cp=5&gs_id=1i&xhr=t&q=foo+bar&pf=p&sclient=psy-ab&oq=foo+b&aq=&aqi=&aql=&gs_l=&pbx=1&bav=on.2,or.r_gc.r_pw.r_cp.r_qf.,cf.osb&fp=f191a14c9679b78&biw=927&bih=1095"""
        self.assertEqual(mm.normalize_url(url), u"""www.google.co.jp/#q=foo+bar""")
        
        url = u"""http://www.google.co.jp/search?client=ubuntu&channel=fs&q=foo+bar&ie=utf-8&oe=utf-8&hl=ja#hl=ja&client=ubuntu&hs=akZ&channel=fs&sclient=psy-ab&q=foo+bar&oq=foo+bar&aq=f&aqi=&aql=&gs_l=serp.3...0l0l0l29454l0l0l0l0l0l0l0l0ll0l0.frgbld.&pbx=1&bav=on.2,or.r_gc.r_pw.r_qf.,cf.osb&fp=ea013b4510645c1f&biw=962&bih=1026"""
        self.assertEqual(mm.normalize_url(url), u"""www.google.co.jp/search?q=foo+bar&q=foo+bar""")
        
        url = u"""http://scholar.google.co.jp/scholar?q=foo+bar&hl=ja&btnG=%E6%A4%9C%E7%B4%A2&lr="""
        self.assertEqual(mm.normalize_url(url), u"""scholar.google.co.jp/scholar?q=foo+bar""")
        
        url = u"""http://www.youtube.com/watch?v=mFbkPWu6clM&feature=disco&playnext=1&list=AVTGnpyrBl25xvQpqP7QzSFersQ1EbW-gM"""
        self.assertEqual(mm.normalize_url(url), u"""www.youtube.com/watch?v=mFbkPWu6clM""")

        url = u"""http://www.youtube.com/results?search_query=thomas&oq=thomas&aq=f&aqi=p-p1g9&aql=&gs_l=youtube-psuggest.3..35i39j0l9.79967l80756l0l80955l6l6l0l0l0l0l88l479l6l6l0."""
        self.assertEqual(mm.normalize_url(url), u"""www.youtube.com/results?search_query=thomas""")
        
        url = u"""twitter.com/#!/tos_kamiya/123"""
        self.assertEqual(mm.normalize_url(url), u"""twitter.com/tos_kamiya/123""")

    def test_merge_url_by_last_param(self):
        urls = [
            (1, "http://hoge.com/view=itemname&page=1"), 
            (1, "http://hoge.com/view=itemname&page=2")
        ]
        mergedUrls = mm.merge_url_by_last_param(urls)
        self.assertEqual(mergedUrls, [
            (1, "http://hoge.com/view=itemname&{page=1,page=2}"), 
        ])
        
        urls = [
            (1, "http://hoge.com/view=itemname&page=1"), 
            (2, "http://hoge.com/view=itemname&page=2")
        ]
        mergedUrls = mm.merge_url_by_last_param(urls)
        self.assertEqual(mergedUrls, urls)

        urls = [
            (1, "http://hoge.com/view=itemname&page=1"), 
            (1, "http://hoge.com/view=itemname&date=2")
        ]
        mergedUrls = mm.merge_url_by_last_param(urls)
        self.assertEqual(mergedUrls, [
            (1, "http://hoge.com/view=itemname&{page=1,date=2}"), 
        ])
        
        urls = [
            (1, "http://hoge.com/view=itemname&page=1"), 
            (1, "http://hoge.com/view=anotheritem&page=2")
        ]
        mergedUrls = mm.merge_url_by_last_param(urls)
        self.assertEqual(mergedUrls, [
            (1, "http://hoge.com/view=itemname&page=1"), 
            (1, "http://hoge.com/view=anotheritem&page=2")
        ])
        
    def test_merge_url_2(self):
        urls = [
            (1, "http://hoge.com/foo"), 
            (1, "http://hoge.com/bar")
        ]
        mergedUrls = mm.merge_url_by_last_param(urls)
        self.assertEqual(mergedUrls, [
            (1, "http://hoge.com/{foo,bar}")
        ])
        
        urls = [
            (1, "http://hoge.com/search?q=hoge"), 
            (1, "http://hoge.com/search?q=fuga")
        ]
        mergedUrls = mm.merge_url_by_last_param(urls)
        self.assertEqual(mergedUrls, [
            (1, "http://hoge.com/search?{q=hoge,q=fuga}")
        ])


if __name__ == "__main__":
    unittest.main()