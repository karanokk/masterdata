import sqlite3
from copy import deepcopy

from .common import Integrator
from ..exceptions import MismatchedData
from ...utils import flatten
from os import path
import json


class ServantIG(Integrator):
    def __init__(self, con: sqlite3.Connection, fallback_file_dir: str):
        super().__init__(con)
        with open(path.join(fallback_file_dir, 'treasure_device.json')) as td_f:
            td_data = json.load(td_f)
            self.td_ig = ServantTreasureDeviceIG(con, td_data)
        
        with open(path.join(fallback_file_dir, 'skill.json')) as skill_f:
            skill_data = json.load(skill_f)
            self.skill_ig = ServantSkillIG(con, skill_data)
            
        self.class_skill_ig = ServantClassSkillIG(con)
        self.material_ig = ServantMaterialIG(con)
        self.comment_ig = ServantCommentIG(con)

    def setup(self):
        self.rename_column('mstSvt', name='jpName')
        self.add_column('mstSvt', cnName='TEXT')

    def integrate(self, servant):
        collection_no = servant['collection_no']
        svt_id = self.svt_id(collection_no)

        try:
            self.td_ig.integrate(svt_id, servant['treasure_devices'])
        except MismatchedData as err:
            self.logger.error(f'{servant["name"]}: mismatched treasure devices\n{err.mc_data}\n{err.mst_data}')

        try:
            self.skill_ig.integrate(svt_id, servant['skills'])
        except MismatchedData as err:
            self.logger.error(f'{servant["name"]}: mismatched skills\n{err.mc_data}\n{err.mst_data}')

        self.class_skill_ig.integrate(svt_id, servant['passives'])

        try:
            if svt_id != 800100:
                self.material_ig.integrate(svt_id, servant['ascension_materials'])
            self.material_ig.integrate(svt_id, servant['skill_materials'])
        except MismatchedData as err:
            self.logger.error(f'{servant["name"]}: mismatched materials\n{err.mc_data}\n{err.mst_data}')

        self.comment_ig.integrate(svt_id, servant['bond_stories'])

    def svt_id(self, collection_no):
        sql = 'SELECT id FROM mstSvt WHERE collectionNo=? and (type=1 or type=2 or type=9);'
        res = self.con.execute(sql, (collection_no,)).fetchone()
        return res[0]

    def update_svt_name(self, svt_id, name):
        self.con.execute('UPDATE mstSvt SET cnName=?, WHERE id=?', (name, svt_id))


class ServantTreasureDeviceIG(Integrator):
    def setup(self):
        self.rename_column('mstTreasureDeviceDetail', detail='jpDescriptions')
        self.add_column('mstTreasureDeviceDetail', cnDescriptions='TEXT', levelValues='TEXT')

        self.rename_column('mstTreasureDevice', name='jpName', typeText='jpTypeText')
        self.add_column('mstTreasureDevice', cnName='TEXT', cnTypeText='TEXT')

    def integrate(self, svt_id: int, treasure_devices):
        tds = self._pre_process(treasure_devices)
        has_strengthStatus = len(tds) > len(treasure_devices)
        mst_tds = self.masterdata_treasure_devices(svt_id)

        updated_td_ids = []

        for td in tds:
            title = td['title']
            strength_status = 1 if has_strengthStatus else 0
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
                        td_id, td['name'], td['type_text'])
                    self.update_treasure_device_detail(
                        td_id, td['detail'], td['value'])
                    updated_td_ids.append(td_id)
                    break

        if len(mst_tds) != len(updated_td_ids):
            count = self.fallback(str(svt_id))
            if len(mst_tds) != count: # simple validation
                raise MismatchedData(tds, mst_tds)
    
    @classmethod
    def _pre_process(cls, treasure_devices):
        treasure_devices = sorted(treasure_devices, key=lambda td: td['title'])
        if len(treasure_devices) > 2 and treasure_devices[0]['title'] == '真名解放、强化后':
            # add treasure device(ignored by mooncell)
            new = deepcopy(treasure_devices[0])
            new['name'] = '？？？'
            new['title'] = '强化后'
            treasure_devices.insert(1, new)
        return treasure_devices

    def masterdata_treasure_devices(self, svt_id: int):
        res = self.con.execute(
            'SELECT DISTINCT treasureDeviceId, strengthStatus, flag FROM mstSvtTreasureDevice WHERE svtId=? AND num=1',
            (svt_id,)).fetchall()
        return res

    def update_treasure_device(self, treasure_device_id, name, type_text):
        self.con.execute('UPDATE mstTreasureDevice SET cnName=?, cnTypeText=? WHERE id=?',
                         (name, type_text, treasure_device_id))

    def update_treasure_device_detail(self, treasure_device_id, descriptions, level_values):
        self.con.execute('UPDATE mstTreasureDeviceDetail SET cnDescriptions=?, levelValues=? WHERE id=?',
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
        updated_skill_ids = []

        for skill in skills:
            title = skill['title']
            if title == '强化前':
                strength_status = 1
            elif title == '强化后':
                strength_status = 2
            else:
                strength_status = 0
            num = skill['num']
            flag = 0

            for mst_skill in mst_skills:
                if mst_skill[3] == num and mst_skill[1] == strength_status and mst_skill[2] == flag:
                    skill_id = mst_skill[0]
                    self.update_skill(skill_id, skill['name'])
                    self.update_skill_detail(
                        skill_id, skill['detail'], skill['value'])
                    updated_skill_ids.append(skill_id)
                    break

        if len(mst_skills) != len(updated_skill_ids):
            count = self.fallback(str(svt_id))
            if len(mst_skills) != count: # simple validation
                raise MismatchedData(skills, mst_skills)

    def masterdata_skills(self, svt_id: int):
        res = self.con.execute('SELECT DISTINCT skillId, strengthStatus, flag, num FROM mstSvtSkill WHERE svtId=?',
                               (svt_id,)).fetchall()
        return res

    def update_skill(self, skill_id, name):
        self.con.execute(
            'UPDATE mstSkill SET cnName=? WHERE id=?', (name, skill_id))

    def update_skill_detail(self, skill_id, descriptions, level_values):
        self.con.execute('UPDATE mstSkillDetail SET cnDescriptions=?, levelValues=? WHERE id=?',
                         (descriptions, level_values, skill_id))


class ServantClassSkillIG(ServantSkillIG):
    def setup(self):
        pass

    def integrate(self, svt_id: int, skills):
        class_passive_ids = self.masterdata_class_passive_ids(svt_id)
        for skill_id, skill in zip(class_passive_ids, skills):
            self.update_skill(skill_id, skill['name'])
            self.update_skill_detail(
                skill_id, skill['detail'], skill['value'])

    def masterdata_class_passive_ids(self, svt_id):
        res = self.con.execute('SELECT classPassive as "classPassive [intList]" FROM mstSvt WHERE id=?',
                               (svt_id,)).fetchone()
        return res[0] if res else []


class ServantMaterialIG(Integrator):
    def setup(self):
        self.rename_column('mstItem', name='jpName')
        self.add_column('mstItem', cnName='TEXT')

    def integrate(self, svt_id: int, masterials):
        if not masterials:
            return
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
        if len(names) != len(item_ids):
            raise MismatchedData(names, item_ids)
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
        self.rename_column('mstSvtComment', comment='jpComment')
        self.add_column('mstSvtComment', cnComment='TEXT')

    def integrate(self, svt_id: int, comments):
        for index, comment in enumerate(comments):
            self.update_comment(svt_id, index + 1, comment[1])

    def update_comment(self, svt_id, index, comment):
        self.con.execute('UPDATE mstSvtComment SET cnComment=? WHERE svtId=? and id=?',
                         (comment, svt_id, index))
