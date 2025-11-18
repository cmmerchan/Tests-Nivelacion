import cloudinary
import cloudinary.uploader
import undetected_chromedriver as uc
import requests

# Configuración: reemplaza con tus credenciales
cloudinary.config( 
  cloud_name = "damxhjexq", 
  api_key = "666327123749517", 
  api_secret = "OmlSo-CQvDZOxPgj29fm4wGJUR0"
)

folder_path = "NIVELACION 2025 2S/UNIDAD 2/MATEMÁTICAS"

class CloudinaryHandler:
    @staticmethod
    def upload_image(image_path: str, driver:uc.Chrome) -> str:
        selenium_cookies = driver.get_cookies()
        session = requests.Session()

        for cookie in selenium_cookies:
            session.cookies.set(cookie['name'], cookie['value'])
            
        try:
            r = session.get(image_path)
    
            if r.status_code == 200:
                img_bytes = r.content

            response = cloudinary.uploader.upload(
                img_bytes,
                folder=folder_path,
                overwrite=True,
                resource_type="image"
            )
            return response.get("secure_url", "")
        except Exception as e:
            print(f"Error uploading image {image_path}: {e}")
            return ""

