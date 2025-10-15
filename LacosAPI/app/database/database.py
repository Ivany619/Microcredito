import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/MasterLacosMicrocredito")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    # Set client encoding to UTF-8 to handle Portuguese characters properly
    conn.set_client_encoding('UTF8')
    return conn

def create_funcionarios_table():
    """Create funcionarios table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'funcionarios'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Create funcionarios table
            cursor.execute("""
                CREATE TABLE funcionarios (
                    funcionario_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    username text NOT NULL UNIQUE,
                    senha text NOT NULL,
                    nome_completo text NOT NULL,
                    email text NOT NULL UNIQUE,
                    telefone text,
                    nivel_acesso text NOT NULL CHECK (nivel_acesso IN ('Administrador', 'Gestor', 'Operador', 'Consultor')),
                    data_cadastro timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login timestamp with time zone,
                    ativo boolean DEFAULT TRUE,
                    tentativas_login integer DEFAULT 0,
                    bloqueado boolean DEFAULT FALSE,
                    data_bloqueio timestamp with time zone
                );
            """)
            
            # Insert default admin user
            from app.utils.auth import get_password_hash
            admin_password = get_password_hash("admin123")
            
            cursor.execute("""
                INSERT INTO funcionarios (username, senha, nome_completo, email, nivel_acesso, ativo)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, ("admin", admin_password, "Administrador Sistema", "admin@lacos.com", "Administrador", True))
            
            conn.commit()
            print("Funcionarios table created successfully with default admin user")
        else:
            print("Funcionarios table already exists")
            
    except Exception as e:
        print(f"Error creating funcionarios table: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()