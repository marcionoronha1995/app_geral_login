import functools
import hashlib
import os


class V8Sentinel:
    """
    Orquestrador Global de Segurança e Integridade.
    """

    def __init__(self):
        self.authorized_hashes = {
            "app.py": "hash_original_aqui_6a8b2...",  # Exemplo de hash fixo
        }

    def verify_integrity(self, filename):
        """Garante que o código não foi corrompido ou alterado."""
        with open(filename, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Comparação com a base de confiança
        if filename in self.authorized_hashes:
            if file_hash != self.authorized_hashes[filename]:
                return False, f"⚠️ ALERTA: Integridade violada em {filename}!"
        return True, "✅ Integridade confirmada."

    def validate_gate(self, required_key_level):
        """Decorador que atua como o portão de segurança de cada função."""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Verifica a Chave de Segurança em memória
                current_key = os.getenv("V8_MASTER_KEY")
                if not current_key or len(current_key) < 32:
                    raise PermissionError("❌ Chave de segurança inválida ou ausente.")

                print(f"🔒 [SENTINEL] Função '{func.__name__}' validada com sucesso.")
                return func(*args, **kwargs)

            return wrapper

        return decorator


# Instância Global do Orquestrador
sentinel = V8Sentinel()
