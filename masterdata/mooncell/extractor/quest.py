import re

from .common import MooncellIE


class QuestIE(MooncellIE):
    ch_num_map = {
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '十': 10
    }

    def chint(self, s):
        length = len(s)
        if length == 1:
            return self.ch_num_map[s]
        elif length == 2:
            return self.ch_num_map[s[0]] + self.ch_num_map[s[1]]
        elif length == 3:
            return self.ch_num_map[s[0]] * 10 + self.ch_num_map[s[-1]]
        raise ValueError()

    def extract_main_quests(self):
        mains = []
        index = 0
        for table in self.tables_between(self._wikitable_logo, '主线关卡'):
            name = table.xpath('string(tbody/tr[1]/th/big)')
            node = table.getprevious()
            while 1:
                if node is None:
                    return mains
                if node.tag == 'h3':
                    section = node.xpath('string()')
                    if len(section) < 1:
                        index = 0
                    if section.startswith('第'):
                        section = section[1:-1]
                        try:
                            index = int(section)
                        except ValueError:
                            try:
                                index = self.chint(section)
                            except:
                                index = 0
                    else:
                        if index == 0:
                            pass
                        else:
                            index += 1
                    break
                elif node.tag == 'h2':
                    index = 0
                    break
                node = node.getprevious()
            else:
                raise Exception()
            quest = {
                'chapterSubId': index,
                'name': name,
            }
            mains.append(quest)
        return mains

    def extract_free_quests(self):
        frees = []
        index = 1
        for table in self.tables_between(self._wikitable_logo, '自由关卡'):
            index_ele = table.getprevious()
            while 1:
                if index_ele is None:
                    return frees
                if index_ele.tag == 'h3':
                    break
                index_ele = index_ele.getprevious()
            else:
                return frees

            pat = re.compile(r'[（\(]')
            spot = re.split(pat, index_ele.xpath('string()'), 1)[0]
            title = table.xpath('string(tbody/tr[1]/th/big)')
            quest = {
                'chapterSubId': index,
                'name': title,
                'spotName': spot
            }
            frees.append(quest)
            index += 1
        return frees
