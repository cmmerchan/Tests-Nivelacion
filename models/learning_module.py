# from models.english_level import Level

class LearningModule:
    # def __init__(self, level: str, unit: str, sub_unit: str):
    #     self.level = level
    #     self.unit = unit
    #     self.sub_unit = sub_unit
    
    def __init__(self):
        self.level = ""
        self.unit = ""
        self.sub_unit = ""

    def to_dict(self):
        return {
            "level": self.level,
            "unit": self.unit,
            "sub_unit": self.sub_unit
        }