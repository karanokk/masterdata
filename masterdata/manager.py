import sqlite3


class MasterDatabaseManager:
    def __init__(self, con: sqlite3.Connection):
        self.con = con

    """Custom"""

    def servant_infos(self):
        res = self.con.execute(
            "SELECT id, collectionNo, name FROM mstSvt WHERE collectionNo>0 and (type=1 or id=800100) "
            "ORDER BY collectionNo").fetchall()
        return res

    def main_quest_infos(self):
        res = self.con.execute(
            'select id, jpName from mstQuest where type=1 AND id<93000000').fetchall()
        return res

    def free_quest_infos(self):
        res = self.con.execute(
            'select id, jpName from mstQuest where type=2 and id<94000000').fetchall()
        return res

    def treasure_device_id_matcher(self, svt_id):
        res = self.con.execute(
            "SELECT treasureDeviceId, strengthStatus, flag FROM mstSvtTreasureDevice WHERE svtId=? AND num=1",
            (svt_id,)).fetchall()

        def match(strength_status, flag):
            for treasure_device in res:
                if treasure_device[1] == strength_status and treasure_device[2] == flag:
                    return treasure_device[0]
        return match, len(res)

    def skill_id_matcher(self, svt_id):
        res = self.con.execute("SELECT skillId, strengthStatus, flag, num FROM mstSvtSkill WHERE svtId=?",
                               (svt_id,)).fetchall()

        def match(num, strength_status, flag):
            for skill in res:
                if skill[3] == num and skill[1] == strength_status and skill[2] == flag:
                    return skill[0]
        return match, len(res)

    """Read"""

    def servant_id(self, no: int):
        res = self.con.execute(
            "SELECT id FROM mstSvt WHERE collectionNo=? and (type=1 or id=800100) LIMIT 1",
            (no,)).fetchone()
        if res:
            return res[0]
        else:
            raise Exception(f'Unknown servant with No.{no}')

    def spot_id(self, quest_id: int):
        res = self.con.execute(
            "select spotId from mstQuest where id=?", (quest_id,)).fetchone()
        return res[0]

    def passive_ids(self, svt_id):
        res = self.con.execute('SELECT classPassive as "classPassive [intList]" FROM mstSvt WHERE id=?',
                               (svt_id,)).fetchone()
        return res[0] if res else []

    def related_quest_ids(self, svt_id):
        res = self.con.execute('select relateQuestIds as "relateQuestIds [intList]" from mstSvt where id=?',
                               (svt_id,)).fetchone()
        return res[0] if res else []

    def ascension_item_ids(self, svt_id):
        res = self.con.execute('SELECT itemIds as "itemIds [intList]" FROM mstCombineLimit WHERE id=? '
                               'ORDER BY svtLimit LIMIT 4',
                               (svt_id,)).fetchall()
        return [one[0] for one in res]

    def skill_item_ids(self, svt_id):
        res = self.con.execute('SELECT itemIds as "itemIds [intList]" FROM mstCombineSkill WHERE id=? '
                               'ORDER BY skillLv LIMIT 9',
                               (svt_id,)).fetchall()
        return [one[0] for one in res]

    """Update"""

    def update_name(self, svt_id, name):
        self.con.execute(
            "UPDATE mstSvt SET cnName=? WHERE id=?", (svt_id, name))

    def update_item_name(self, item_id, name):
        self.con.execute(
            "UPDATE mstItem SET cnName=? WHERE id=?", (item_id, name))

    def update_quest_name(self, quest_id, name):
        self.con.execute(
            "UPDATE mstQuest SET cnName=? WHERE id=?", (quest_id, name))

    def update_svt_comment(self, svt_id, comment_id, comment):
        self.con.execute(
            'UPDATE mstSvtComment SET comment=? WHERE svtId=? and id=?', (comment, svt_id, comment_id))

    def update_spot_name(self, spot_id, name):
        self.con.execute(
            "UPDATE mstSpot SET cnName=? WHERE id=?", (spot_id, name))

    def update_treasure_device(self, treasure_device_id, name, type_text):
        self.con.execute("UPDATE mstTreasureDevice SET cnName=?, cnTypeText=? WHERE id=?",
                         (name, type_text, treasure_device_id))

    def update_treasure_device_detail(self, treasure_device_id, descriptions, level_values):
        self.con.execute("UPDATE mstTreasureDeviceDetail SET cnDescriptions=?, levelValues=? WHERE id=?",
                         (descriptions, level_values, treasure_device_id))

    def update_skill(self, skill_id, name):
        self.con.execute(
            "UPDATE mstSkill SET cnName=? WHERE id=?", (name, skill_id))

    def update_skill_detail(self, skill_id, descriptions, level_values):
        self.con.execute("UPDATE mstSkillDetail SET cnDescriptions=?, levelValues=? WHERE id=?",
                         (descriptions, level_values, skill_id))

    def update_comment(self, svt_id, comment_id, comment):
        self.con.execute(
            'UPDATE mstSvtComment SET jpComment=? WHERE svtId=? and id=?', (comment, svt_id, comment_id))
