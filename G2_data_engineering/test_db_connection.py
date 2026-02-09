import os
import psycopg2
import time

def get_connection():
    """
    يسترجع اتصال قاعدة البيانات.
    في بيئة Docker، يجب أن يكون الهوست هو اسم خدمة قاعدة البيانات (sdid_postgres)
    والمنفذ هو المنفذ الداخلي (5432).
    """
    try:
        # إعدادات الاتصال: نستخدم 'sdid_postgres' كقيمة افتراضية للهوست داخل دوكر
        # إذا كنت تشغل الكود محلياً (خارج دوكر)، قد تحتاج لتغيير القيم أو استخدام متغيرات البيئة
        db_host = os.getenv("DB_HOST", "sdid_postgres") 
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "sdid_db")
        db_user = os.getenv("DB_USER", "sdid_user")
        db_password = os.getenv("DB_PASSWORD", "sdid_password")

        print(f"🔌 Connecting to DB at {db_host}:{db_port}...")

        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return conn
    except Exception as e:
        # طباعة الخطأ بوضوح للمساعدة في التشخيص
        print(f"❌ Error details: {e}")
        raise RuntimeError(f"❌ Impossible de se connecter à PostgreSQL ({db_host}:{db_port})")

if __name__ == "__main__":
    # اختبار سريع عند تشغيل الملف مباشرة
    try:
        conn = get_connection()
        print("✅ Connexion réussie !")
        conn.close()
    except Exception as e:
        print(e)