import functools
import hashlib
import os
import json
import pathlib

from src.backend.core.exceptions import V8SecurityException

try:
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import serialization, hashes
except ImportError:
    # Caso cryptography falhe em carregar em produção
    padding = None
    serialization = None
    hashes = None


class V8Sentinel:
    """
    Orquestrador Global de Segurança e Integridade.
    """

    def verify_integrity(self):
        """Garante que nenhum arquivo foi corrompido ou alterado no servidor."""
        if padding is None:
            raise V8SecurityException("❌ Erro de Sistema: Dependências de criptografia ausentes.")

        root = pathlib.Path(__file__).resolve().parent
        metadata_dir = root / "src" / "backend" / "core" / "metadata"
        
        pub_path = metadata_dir / "public_key.pem"
        sig_path = metadata_dir / "signature.json"
        
        if not pub_path.exists():
            raise V8SecurityException("❌ Erro de Integridade: Chave pública não encontrada no servidor.")
        
        if not sig_path.exists():
            raise V8SecurityException("❌ Erro de Integridade: Manifesto de assinatura não encontrado.")
        
        # 1. Carrega a chave pública RSA
        try:
            with open(pub_path, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
        except Exception as e:
            raise V8SecurityException(f"❌ Erro de Sistema: Falha ao carregar a chave pública. {e}")
            
        # 2. Carrega a assinatura e o manifesto de hashes
        try:
            with open(sig_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            raise V8SecurityException(f"❌ Erro de Integridade: Falha ao ler assinatura do manifesto. {e}")
            
        manifest = payload.get("manifest", {})
        signature_hex = payload.get("signature_hex", "")
        
        if not manifest or not signature_hex:
            raise V8SecurityException("❌ Erro de Integridade: Assinatura corrompida ou inválida.")
            
        # 3. Valida a assinatura digital do manifesto
        try:
            manifest_data = json.dumps(manifest, sort_keys=True).encode("utf-8")
            signature = bytes.fromhex(signature_hex)
            
            public_key.verify(
                signature,
                manifest_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except Exception as e:
            raise V8SecurityException(f"❌ Falha de Assinatura: O manifesto de segurança foi corrompido ou violado! {e}")
            
        # 4. Valida o hash SHA-256 de cada arquivo individualmente
        for rel_path, expected_hash in manifest.items():
            file_path = root / rel_path
            if not file_path.exists():
                raise V8SecurityException(f"❌ Falha de Integridade: Arquivo essencial ausente: {rel_path}")
                
            # Calcula o hash atual do arquivo
            sha = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
            current_hash = sha.hexdigest()
            
            if current_hash != expected_hash:
                raise V8SecurityException(f"❌ Falha de Integridade: O arquivo foi alterado no servidor: {rel_path}")
                
        return True

    def validate_gate(self, required_key_level):
        """Decorador que atua como o portão de segurança de cada função."""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Verifica a Chave de Segurança em memória
                current_key = os.getenv("V8_MASTER_KEY")
                if not current_key or len(current_key) < 32:
                    raise V8SecurityException("❌ Chave de segurança inválida ou ausente.")

                print(f"🔒 [SENTINEL] Função '{func.__name__}' validada com sucesso.")
                return func(*args, **kwargs)

            return wrapper

        return decorator


# Instância Global do Orquestrador
sentinel = V8Sentinel()
