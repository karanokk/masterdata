import sqlite3
from copy import deepcopy

from .common import Integrator
from ...utils import flatten


class ServantIG(Integrator):
    def __init__(self, con: sqlite3.Connection):
        super().__init__(con)

        self.td_ig = ServantTreasureDeviceIG(con)
        self.skill_ig = ServantSkillIG(con)
        self.class_skill_ig = ServantClassSkillIG(con)
        self.material_ig = ServantMaterialIG(con)
        self.comment_ig = ServantCommentIG(con)

    def integrate(self, servant):
        collection_no = servant["collection_no"]
        svt_id = self.svt_id(collection_no)
        self.td_ig.integrate(svt_id, servant["treasure_devices"])
        self.skill_ig.integrate(svt_id, servant["skills"])
        self.class_skill_ig.integrate(svt_id, servant["passives"])
        self.material_ig.integrate(svt_id, servant["ascension_materials"])
        self.material_ig.integrate(svt_id, servant["skill_materials"])
        # self.comment_ig.integrate(svt_id, servant["stories"])

    def svt_id(self, collection_no):
        sql = """SELECT id FROM mstSvt WHERE collectionNo=? and (type=1 or type=2);"""
        res = self.con.execute(sql, (collection_no,)).fetchone()
        return res[0]


class ServantTreasureDeviceIG(Integrator):

    def setup(self):
        self.rename_column('mstTreasureDeviceDetail', detail='jpDescriptions')
        self.add_column('mstTreasureDeviceDetail', cnDescriptions='TEXT', levelValues='TEXT')

        self.rename_column('mstTreasureDevice', name='jpName', typeText='jpTypeText')
        self.add_column('mstTreasureDevice', cnName='TEXT', cnTypeText='TEXT')

    def integrate(self, svt_id: int, treasure_devices):
        tds = self._pre_process(treasure_devices)
        mst_tds = self.masterdata_treasure_devices(svt_id)

        if len(mst_tds) != len(tds):
            self.logger.warning(
                f'Treasure devices count not match: [mooncell: database] = [{len(tds)} : {mst_tds}]')

        for td in tds:
            title = td["title"]
            strength_status = 0
            flag = 0
            if title == '强化前':
                strength_status = 1
            elif title == '强化后':
                strength_status = 2
            elif title == '真名解放前':
                flag = 0
            elif title == '真名解放后':
                flag = 2
            elif title == '真名解放、强化后':
                flag = 2
                strength_status = 2

            for mst_td in mst_tds:
                if mst_td[1] == strength_status and mst_td[2] == flag:
                    td_id = mst_td[0]
                    self.update_treasure_device(
                        td_id, td["name"], td["typeText"])
                    self.update_treasure_device_detail(
                        td_id, td["detail"], td["value"])
                    break

    @classmethod
    def _pre_process(cls, treasure_devices):
        treasure_devices = sorted(treasure_devices, key=lambda td: td["title"])
        first = treasure_devices[0]
        if len(treasure_devices) > 2 and first['title'] == '真名解放、强化后':
            # add treasure device(ignored by mooncell)
            new = deepcopy(first)
            new["name"] = '？？？'
            new["title"] = '强化后'
            treasure_devices.insert(1, new)
        return treasure_devices

    def masterdata_treasure_devices(self, svt_id: int):
        res = self.con.execute(
            "SELECT treasureDeviceId, strengthStatus, flag FROM mstSvtTreasureDevice WHERE svtId=? AND num=1",
            (svt_id,)).fetchall()
        return res

    def update_treasure_device(self, treasure_device_id, name, type_text):
        self.con.execute("UPDATE mstTreasureDevice SET cnName=?, cnTypeText=? WHERE id=?",
                         (name, type_text, treasure_device_id))

    def update_treasure_device_detail(self, treasure_device_id, descriptions, level_values):
        self.con.execute("UPDATE mstTreasureDeviceDetail SET cnDescriptions=?, levelValues=? WHERE id=?",
                         (descriptions, level_values, treasure_device_id))


class ServantSkillIG(Integrator):
    def setup(self):
        self.rename_column('mstSkillDetail', detail='jpDescriptions')
        self.add_column('mstSkillDetail',
                        cnDescriptions='TEXT', cnTypeText='TEXT', levelValues='TEXT')

        self.rename_column('mstSkill', name='jpName')
        self.add_column('mstSkill', cnName='TEXT')

    def integrate(self, svt_id: int, skills):
        mst_skills = self.masterdata_skills(svt_id)

        if len(mst_skills) != len(skills):
            self.logger.warning(
                f'Skills count not match: [mooncell: database] = [{len(skills)} : {len(mst_skills)}]')
        for skill in skills:
            title = skill["title"]
            strength_status = 0
            if title == '强化前':
                strength_status = 1
            elif title == '强化后':
                strength_status = 2
            num = skill["num"]
            flag = 0

            for mst_skill in mst_skills:
                if mst_skill[3] == num and mst_skill[1] == strength_status and mst_skill[2] == flag:
                    skill_id = mst_skill[0]
                    self.update_skill(skill_id, skill["name"])
                    self.update_skill_detail(
                        skill_id, skill["detail"], skill["value"])

    def masterdata_skills(self, svt_id: int):
        res = self.con.execute("SELECT skillId, strengthStatus, flag, num FROM mstSvtSkill WHERE svtId=?",
                               (svt_id,)).fetchall()
        return res

    def update_skill(self, skill_id, name):
        self.con.execute(
            "UPDATE mstSkill SET cnName=? WHERE id=?", (name, skill_id))

    def update_skill_detail(self, skill_id, descriptions, level_values):
        self.con.execute("UPDATE mstSkillDetail SET cnDescriptions=?, levelValues=? WHERE id=?",
                         (descriptions, level_values, skill_id))


class ServantClassSkillIG(ServantSkillIG):
    def setup(self):
        pass

    def integrate(self, svt_id: int, skills):
        class_passive_ids = self.masterdata_class_passive_ids(svt_id)
        for skill_id, skill in zip(class_passive_ids, skills):
            self.update_skill(skill_id, skill["name"])
            self.update_skill_detail(
                skill_id, skill["detail"], skill["value"])

    def masterdata_class_passive_ids(self, svt_id):
        res = self.con.execute('SELECT classPassive as "classPassive [intList]" FROM mstSvt WHERE id=?',
                               (svt_id,)).fetchone()
        return res[0] if res else []


class ServantMaterialIG(Integrator):
    def setup(self):
        self.rename_column('mstItem', name='jpName')
        self.add_column('mstItem', cnName='TEXT')

    def integrate(self, svt_id: int, masterials):
        if len(masterials) < 5:
            self.update_ascension_materials(svt_id, masterials)
        else:
            self.update_skill_materials(svt_id, masterials)

    def masterdata_ascension_item_ids(self, svt_id):
        res = self.con.execute('SELECT itemIds as "itemIds [intList]" FROM mstCombineLimit WHERE id=? '
                               'ORDER BY svtLimit LIMIT 4',
                               (svt_id,)).fetchall()
        return [one[0] for one in res]

    def masterdata_skill_item_ids(self, svt_id):
        res = self.con.execute('SELECT itemIds as "itemIds [intList]" FROM mstCombineSkill WHERE id=? '
                               'ORDER BY skillLv LIMIT 9',
                               (svt_id,)).fetchall()
        return [one[0] for one in res]

    def _update_material(self, item_ids, name_groups):
        item_ids = flatten(item_ids)
        names = flatten(name_groups)
        assert len(names) == len(item_ids)
        self.con.executemany(
            'UPDATE mstItem SET cnName=? WHERE id=?', zip(names, item_ids))

    def update_ascension_materials(self, svt_id, name_groups):
        item_ids = self.masterdata_ascension_item_ids(svt_id)
        self._update_material(item_ids, name_groups)

    def update_skill_materials(self, svt_id, name_groups):
        item_ids = self.masterdata_skill_item_ids(svt_id)
        self._update_material(item_ids, name_groups)


class ServantCommentIG(Integrator):
    def setup(self):
        self.rename_column('mstSvtComment', name='jpComment')
        self.add_column('mstSvtComment', cnComment='TEXT')

    def integrate(self, svt_id: int, comments):
        for index, comment in enumerate(comments):
            self.update_comment(svt_id, index + 1, comment)

    def update_comment(self, svt_id, index, comment):
        self.con.execute('UPDATE mstSvtComment SET cnComment=? WHERE svtId=? and id=?',
                         (comment, svt_id, index))
