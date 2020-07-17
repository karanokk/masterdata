import re

from .common import MooncellIE


class ServantIE(MooncellIE):
    def extract_basic_data(self):
        table = next(self.tables_between(self._wikitable_nomobile, '基础数值'))
        nick_names = self.root.xpath(
            'string(/html/head/meta[@name="keywords"]/@content)').split(',')
        if nick_names and nick_names[0] == '{{{昵称}}}':
            nick_names = []
        name = table.xpath('string(tbody/tr[1]/th[1])').rstrip('\n')
        if '/' in name:  # 织田信长/织田吉法师/魔王信长
            name = name.split('/')[0]
        res = table.xpath('tbody/tr[1]/th[2]/text()')[0].rstrip('\n')
        if not res:
            res = table.xpath('tbody/tr[3]/th/text()')[0].rstrip('\n')
        collection_no = int(res[3:])
        cv = table.xpath('tbody/tr[5]/td[2]/a/text()')[0]
        illustrator = table.xpath('tbody/tr[5]/td[1]/a/text()')[0]
        del table, res, self
        return locals()

    @staticmethod
    def _extract_level_effects(trs):
        effects = []
        level_values = []
        for tr in trs:
            if tr[0].tag == 'th':
                name = tr.xpath('string(th)').rstrip('\n')
                effects.append(name)
            else:
                value = [v.rstrip('\n') for v in tr.xpath('td//text()')]
                level_values.append(value)
        assert len(effects) == len(level_values)
        return effects, level_values

    def extract_treasure_devices(self):
        tables = self.tables_between(self._wikitable_nomobile_logo, '宝具')

        def is_special(table):
            title = table.getparent().get('title')
            return title and (title.endswith('限定') or title.startswith('灵基再临'))

        tds = [self._extract_treasure_device(
            table) for table in tables if not is_special(table)]
        return tds

    @classmethod
    def _extract_treasure_device(cls, table):
        trs = table.xpath('tbody/tr')
        title = table.getparent().get('title')
        name = trs[0].xpath('string(td/div/big)')
        type_text = trs[0].xpath('string(th/p[last()])')
        effects, level_values = cls._extract_level_effects(
            trs[2 - len(trs) % 2:])
        del trs, table, cls
        return locals()

    def extract_skills(self):
        tables = self.tables_between(
            self._wikitable_nomobile_logo, '持有技能', keep_struct=True)
        skills = []
        for index, items in enumerate(tables, 1):
            if not isinstance(items, list):
                items = [items]
            for table in items:
                skills.append(self._extract_skills(table, index))
        return skills

    @classmethod
    def _extract_skills(cls, table, num):
        trs = table.xpath('tbody/tr')
        name = trs[0].xpath('string(th[2])').rstrip('\n')
        title = table.getparent().get('title')
        effects, level_values = cls._extract_level_effects(trs[2:])
        del trs, cls
        return locals()

    def extract_class_skills(self):
        tables = self.tables_between(
            self._wikitable_nomobile_logo, '职阶技能', keep_struct=True)

        class_skills = []
        for table in tables:
            if isinstance(table, list):
                table = table[0]
            trs = table.xpath('tbody/tr')
            name = None
            for tr in trs:
                if tr[0].tag == 'th':  # name
                    name = tr.xpath('string(th[2])').rstrip('\n ')
                    level = tr.xpath('string(td)')
                    if level.startswith('固有等级：'):
                        level = level[5:].strip('\n ')
                    name = f'{name} {level}'
                else:
                    detail = re.split('&|＆',
                                      tr.xpath('string(td)').rstrip('\n'))
                    effects = []
                    level_values = []
                    for one in detail:
                        result = re.search(r'\((\d+(\.\d+)?(%)?)\)', one)
                        if result:
                            effects.append(one[:result.span()[0]])
                            level_values.append(result.group(1))
                        else:
                            effects.append(one)
                            level_values.append('∅')
                    class_skill = {'num': -1, 'name': name,
                                   'effects': effects, 'level_values': level_values}
                    class_skills.append(class_skill)
                    name = None
        return class_skills

    @staticmethod
    def _extract_materials(table):
        # remove last row for total material
        trs = table.xpath('tbody/tr')[:-1]
        titles = ((td.xpath('descendant::a/@title') for td in tr.xpath('td'))
                  for tr in trs)
        item_names = []
        # sort
        for row in zip(*titles):
            item_names += row
        return item_names

    def extract_skill_materials(self):
        for table in self.tables_between(self._wikitable_nomobile, '技能强化'):
            return self._extract_materials(table)
        return []

    def extract_ascension_materials(self):
        for table in self.tables_between(self._wikitable_nomobile, '灵基再临（从者进化）'):
            return self._extract_materials(table)
        return []

    def extract_bond_stories(self):
        tables = self.tables_between(self._wikitable, '资料')
        stories = [self._extract_bond_stories(
            table) for table in tables if table.getprevious().get('class')]
        return stories

    @staticmethod
    def _extract_bond_stories(table):
        trs = table.xpath('tbody/tr')
        assert (len(trs) == 2)
        condition = trs[0].xpath('string(th)').rstrip('\n')
        story = trs[1].xpath('string(td/div/div/p)').rstrip('\n')
        del trs, table
        return locals()

    def extract_dialogues(self):
        tables = self.tables_between(self._mw_wikitable_nomobile, '语音')
        dialogues = [dialogue for dialogue in [
            self._extract_dialogues(table) for table in tables]]
        return dialogues

    @staticmethod
    def _extract_dialogues(table):
        trs = table.xpath('tbody/tr')
        category = trs[0].xpath('string(th/b)')

        def add_https(s):
            return 'https:' + s if s.startswith('//') else s

        dialogues = [{'category': category, 'stage': tr.xpath('string(th/b)'), 'lines': tr.xpath('string(td[1]/p)'),
                      'audioURL': add_https(tr.xpath('string(td[2]/span/a[last()]/@href)'))} for tr in trs[1:]]
        return dialogues
