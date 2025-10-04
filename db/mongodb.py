from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from utils.constants import Constants
import logging

class MongoDB:
    def __init__(self):
        
        self.logger = logging.getLogger(self.__class__.__name__)  # Logger propio 
        
        self.init_mongodb()
        # self.add_collection(Constants.questionsEnglishTestCollection)
    
    def init_mongodb(self):
        try:
            self.client = MongoClient(Constants.mongodbUrl, server_api=ServerApi('1'))
            self.mongodb = self.client[Constants.dbName]
            self.client.admin.command('ping')  # Confirm connection
            self.logger.info("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            self.logger.error(f"Error connecting to MongoDB: {e}")

    def close(self):
        self.client.close()

    def add_collection(self,name:str):

        if name not in self.mongodb.list_collection_names():
            self.mongodb.create_collection(name)
            self.logger.info(f"Collection '{name}' created")
        else:
            self.logger.info(f"Collection '{name}' already exists.")

    def insert_question(self, collection_name:str ,question_doc: dict):
        collection = self.mongodb[collection_name]

        existing_doc = collection.find_one({
            Constants.questionKey: question_doc[Constants.questionKey]})

        if existing_doc:
            
            self.logger.info(f"ID existente: {existing_doc['_id']}")
            print(existing_doc[Constants.questionKey])
            return existing_doc["_id"]
        else:
            result = collection.insert_one(question_doc)
            self.logger.info(f"Inserted question with _id: {result.inserted_id}")
            return result.inserted_id

    def update_question(self, collection_name:str ,question_id: str, new_answers: list):
        collection = self.mongodb[collection_name]
        result = collection.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": {"answers": new_answers}}
        )
        if result.modified_count > 0:
            self.logger.info(f"Question with _id {question_id} updated successfully.")
        else:
            self.logger.warning(f"No changes made to question with _id {question_id}.")

    def get_question(self,collection_name:str,question:str) -> dict:
        collection = self.mongodb[collection_name]
        question_doc = collection.find_one({Constants.questionKey: {"$regex": question}})
        print(question_doc)
        if question_doc:
            return question_doc
        else:
            self.logger.warning(f"Question '{question}' not found in the database.")
            return None
        
    def generate_pdf(self):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch

        # Configuración de PDF
        page_width, page_height = letter
        left_margin = 1 * inch
        right_margin = 1 * inch
        top_margin = 1 * inch
        bottom_margin = 1 * inch
        max_width = page_width - left_margin - right_margin
        line_height = 14

        # Función para dividir texto en líneas que quepan en el ancho del PDF
        def wrap_text(text, canvas_obj, max_width):
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if canvas_obj.stringWidth(test_line, "Helvetica", 11) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            return lines

        collection = self.mongodb[Constants.questionsEnglishTestCollection]
        # Obtener documentos
        docs = collection.find({}, {"question_type": 1,"question": 1, "answers": 1}).sort("_id")

        # Crear PDF
        c = canvas.Canvas("preguntas_revisar.pdf", pagesize=letter)
        y = page_height - top_margin
        question_number = 1

        for doc in docs:
            question = doc.get("question", "").replace("\n", " ").strip()
            answers = ", ".join(doc.get("answers", []))
            enunciado = doc.get("question_type", "").replace("\n", " ").strip()

            question_lines = wrap_text(f"{question_number}. {question}", c, max_width)
            answer_lines = wrap_text(f"➜ Respuesta: {answers}", c, max_width)
            enunciado_lines = wrap_text(f"➜ Enunciado: {enunciado}", c, max_width)

            required_space = (len(question_lines) + len(answer_lines)+len(enunciado_lines)) * line_height + 10

            if y - required_space < bottom_margin:
                c.showPage()
                y = page_height - top_margin
            
            c.setFont("Helvetica", 9)
            for line in enunciado_lines:
                c.drawString(left_margin, y, line)
                y -= line_height

            c.setFont("Helvetica-Bold", 8)
            for line in question_lines:
                c.drawString(left_margin, y, line)
                y -= line_height

            c.setFont("Helvetica", 8)
            for line in answer_lines:
                c.drawString(left_margin, y, line)
                y -= line_height            

            y -= 10
            question_number += 1

        c.save()
        print("PDF generado: preguntas_revisar.pdf")

    # def update(self):
    #     collection = self.mongodb[Constants.questionsEnglishTestCollection]
    #     query = {"answers": {"$type": "array"}}
    #     docs = collection.find(query)
        
    #     for doc in docs:
    #         answers = doc.get("answers", [])
    #         # Verificamos si es una lista de listas
    #         if answers and isinstance(answers[0], list):
    #             # Aplanamos solo la primera sublista (si eso es lo que quieres)
    #             new_answers = answers[0]
    #             collection.update_one(
    #                 {"_id": doc["_id"]},
    #                 {"$set": {"answers": new_answers}}
    #             )
    #             print(f'Documento {doc["_id"]} actualizado.')


    # def update(self):
    #     collection = self.mongodb[Constants.questionsEnglishTestCollection]
    #     docs = collection.find({"question": {"$regex": "Selecciona una respuesta  "}})

    #     for doc in docs:
    #         question_with_placeholder = doc["question"]
    #         answer = doc["answers"][0] if doc["answers"] else None

    #         if not answer:
    #             continue

    #         # Reemplazo exacto para buscar el documento duplicado (donde ya está reemplazada la palabra)
    #         replaced_question = question_with_placeholder.replace("Selecciona una respuesta", f"{answer}")

    #         # Buscamos si ya existe un documento con la versión reemplazada
    #         duplicate = collection.find_one({"question": replaced_question})

    #         if duplicate:
    #             # Eliminamos el duplicado
    #             collection.delete_one({"_id": duplicate["_id"]})
    #             print(f"Documento duplicado eliminado: {duplicate['_id']}")

    #             # Modificamos el original, reemplazando con "_"
    #             updated_question = question_with_placeholder.replace("Selecciona una respuesta  ", "")
    #             collection.update_one(
    #                 {"_id": doc["_id"]},
    #                 {"$set": {"question": updated_question}}
    #             )
    #             print(f"Documento actualizado con guion bajo: {doc['_id']}")

    #     print("Proceso completado.")





