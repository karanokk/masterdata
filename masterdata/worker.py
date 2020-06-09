import logging
import sqlite3
from copy import deepcopy
from math import floor

from .manager import MasterDatabaseManager
from .utils import flatten

logger = logging.getLogger('masterdata.chaldea')


class ChaldeaWorker:
    def __init__(self, manager: MasterDatabaseManager):
        self.manager = manager

    def setup(self):
        con = self.manager.con
        detail_renames = ['mstSkillDetail', 'mstTreasureDeviceDetail']
        for name in detail_renames:
            con.execute(f"ALTER TABLE {name} RENAME detail TO cnDescriptions")
            con.execute(f"ALTER TABLE {name} ADD jpDescriptions TEXT")
            con.execute(f"ALTER TABLE {name} ADD levelValues TEXT")

        name_renames = ['mstSvt', 'mstSkill', 'mstTreasureDevice',
                        'mstQuest', 'mstItem', 'mstCommandCode', 'mstSpot']
        for name in name_renames:
            con.execute(f"ALTER TABLE {name} RENAME name TO jpName")
            con.execute(f"ALTER TABLE {name} ADD cnName TEXT")

        comment_renames = ['mstSvtComment', 'mstCommandCodeComment']
        for name in comment_renames:
            con.execute(f"ALTER TABLE {name} RENAME comment TO jpComment")
            con.execute(f"ALTER TABLE {name} add cnComment TEXT")

        con.execute("ALTER TABLE mstTreasureDevice RENAME typeText TO cnTypeText")
        con.execute("ALTER TABLE mstTreasureDevice ADD jpTypeText TEXT")

    def load_servant(self, servant: dict):
        manager = self.manager
        no = servant["collection_no"]
        svt_id = manager.servant_id(no)
        manager.update_name(svt_id, servant["name"])
        self.update_treasure_devices(svt_id, servant["treasure_devices"])
        self.update_skills(svt_id, servant["skills"])
        self.update_class_skills(svt_id, servant["passives"])
        self.update_ascension_materials(svt_id, servant["ascension_materials"])
        self.update_skill_materials(svt_id, servant["skill_materials"])
        if "bond_stories" in servant:
            self.update_stories(svt_id, servant["bond_stories"])

    """Servant"""

    def update_treasure_devices(self, svt_id, treasure_devices):
        treasure_devices = sorted(treasure_devices, key=lambda td: td["title"])
        has_strength_status = False
        treasure_device0 = treasure_devices[0]
        count = len(treasure_devices)
        if count > 2 and treasure_device0["title"] == '真名解放、强化后':
            has_strength_status = True
            treasure_device1 = deepcopy(treasure_device0)
            treasure_device1["name"] = '？？？'
            treasure_device1["title"] = '强化后'
            treasure_devices.insert(1, treasure_device1)

        match, g_count = self.manager.treasure_device_id_matcher(svt_id)
        if g_count != len(treasure_devices):
            logger.warning(
                f'Treasure devices count not match: [mooncell: database] = [{count} : {g_count}]')

        for treasure_device in treasure_devices:
            title = treasure_device["title"]
            strength_status = 1 if has_strength_status else 0
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

            treasure_device_id = match(strength_status, flag)
            self.manager.update_treasure_device(
                treasure_device_id, treasure_device["name"], treasure_device["typeText"])
            self.manager.update_treasure_device_detail(
                treasure_device_id, treasure_device["detail"], treasure_device["value"])

    def update_skills(self, svt_id, skills):
        match, g_count = self.manager.skill_id_matcher(svt_id)
        if g_count != len(skills):
            logger.warning(
                f'Skills count not match: [mooncell: database] = [{len(skills)} : {g_count}]')
        for skill in skills:
            title = skill["title"]
            strength_status = 0
            if title == '强化前':
                strength_status = 1
            elif title == '强化后':
                strength_status = 2
            skill_id = match(skill["num"], strength_status, 0)
            self.manager.update_skill(skill_id, skill["name"])
            self.manager.update_skill_detail(
                skill_id, skill["detail"], skill["value"])

    def update_class_skills(self, svt_id, skills):
        passive_ids = self.manager.passive_ids(svt_id)
        for skill_id, skill in zip(passive_ids, skills):
            self.manager.update_skill(skill_id, skill["name"])
            self.manager.update_skill_detail(
                skill_id, skill["detail"], skill["value"])

    def _update_material(self, item_ids, name_groups):
        item_ids = flatten(item_ids)
        names = flatten(name_groups)
        assert len(names) == len(item_ids)
        self.manager.con.executemany(
            'UPDATE mstItem SET cnName=? WHERE id=?', zip(names, item_ids))

    def update_ascension_materials(self, svt_id, name_groups):
        item_ids = self.manager.ascension_item_ids(svt_id)
        self._update_material(item_ids, name_groups)

    def update_skill_materials(self, svt_id, name_groups):
        item_ids = self.manager.skill_item_ids(svt_id)
        self._update_material(item_ids, name_groups)

    def update_stories(self, svt_id, stories):
        for index, story in enumerate(stories):
            self.manager.update_comment(svt_id, index + 1, story[1])

    """Mission"""
    def update_missions(self):

    def _get_part_range(self):
        min_part_id, max_part_id = self.manager.con.execute(
            'SELECT Min(id), Max(id) FROM mstQuest WHERE id <10000000').fetchone()

        def get_part(n):
            return floor(n / 1000000)

        return get_part(min_part_id), get_part(max_part_id)

    def _get_chapter_range(self, part):
        min_chapter_id, max_chapter_id = self.manager.con.execute(
            f'select  Min(id), Max(id) from mstQuest where id between ? and ?',
            (part * 1000000 - 1, part * 1000000 + 1000)).fetchone()

        def get_chapter(n):
            return floor((n - part * 1000000) / 100)

        return get_chapter(min_chapter_id), get_chapter(max_chapter_id)

    def update_main_quests(self, part, chapter, quests):
        start = part * 1000000 + 100 * chapter - 1
        end = part * 1000000 + 100 * (chapter + 1)
        game_sub_chapters = self.manager.con.execute(
            'select id, chapterSubId, jpName from mstQuest where id between ? and ?', (start, end)).fetchall()
        for questId, chapterSubId, jpName in game_sub_chapters:
            for index, quest in enumerate(quests):
                if quest.chapterSubId == chapterSubId:
                    self.manager.update_quest_name(questId, quest.name)
                    logger.debug(
                        f'{chapterSubId} {quest.name} {jpName}')
                    del quests[index]
                    break
                else:
                    if quest.chapterSubId > chapterSubId:
                        logger.debug(
                            f'Skipped Part{part} Chapter{chapter}.{chapterSubId}')
                        break
                    else:
                        logger.debug(
                            f'Failed to handle Part{part} Chapter{chapter}.{chapterSubId}')
                        break

    def update_free_quests(self, part, chapter, quests):
        def get_start_id(target_part, target_chapter):
            if target_part == 1:
                target_part = 0
            elif target_part == 3:
                target_chapter += 1
            return 93000000 + target_part * 10000 + 100 * target_chapter

        start = get_start_id(part, chapter)
        end = get_start_id(part, chapter + 1)
        game_sub_chapters = self.manager.con.execute(
            'select id, chapterSubId, jpName from mstQuest where id between ? and ?', (start, end)).fetchall()
        assert len(game_sub_chapters) == len(quests)
        for game_quest, quest in zip(game_sub_chapters, quests):
            quest_id, chapter_sub_id, jp_name = game_quest
            self.manager.update_quest_name(quest_id, quest.name)
            spot_id = self.manager.spot_id(quest_id)
            assert (spot_id is not None)
            self.manager.update_spot_name(spot_id, quest.spotName)
            logger.debug(f'{chapter_sub_id} {quest.name} {jp_name}')
