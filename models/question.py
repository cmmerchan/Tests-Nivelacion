from models.learning_module import LearningModule
from bson import ObjectId
from utils.constants import Constants
class Question:
    # def __init__(self, question: str, answers: list[str], activity: str,question_type:str,lesson_module_id:ObjectId):
    #     self.question = question
    #     self.answers = answers
    #     self.activity = activity
    #     self.question_type = question_type
    #     self.lesson_module_id = lesson_module_id

    def __init__(self):
        self.type = ""
        self.question = ""
        self.options = []
        self.answers = []
        self.img_source_question = []
        self.img_source_options = []
        # self.learning_module_id = ObjectId()

    def to_dict(self):
        return {
            Constants.questionKey: self.question,
            Constants.optionsKey: self.options,
            Constants.answersKey: self.answers, 
            Constants.questionTypeKey: self.type,
            Constants.imgSourceQuestionKey: self.img_source_question,
            Constants.imgSourceOptionsKey: self.img_source_options,
            # Constants.learningModuleIdKey: self.learning_module_id if isinstance(self.learning_module_id, ObjectId) else ObjectId(self.learning_module_id)
        }
    
    def __str__(self):
        return (
            f"Question(\n"
            f"  type={self.type},\n"
            f"  question={self.question},\n"
            f"  options={self.options},\n"
            f"  answers={self.answers},\n"
            f"  img_source_question={self.img_source_question},\n"
            f"  img_source_options={self.img_source_options}\n"
            f")"
        )
    
        
