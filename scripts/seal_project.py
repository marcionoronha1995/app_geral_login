import os
import sys
import json
import hashlib
import pathlib

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import serialization, hashes
except ImportError:
    print("❌ ERRO: A biblioteca 'cryptography' não está instalada. Execute 'init_env.py' primeiro.")
    sys.exit(1)


def get_project_root():
    return pathlib.Path(__file__).resolve().parent.parent


def get_file_sha256(filepath):
    """Calcula o hash SHA-256 de um arquivo."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def generate_keys(metadata_dir):
    """Gera o par de chaves RSA se elas não existirem."""
    priv_path = metadata_dir / "private_key.pem"
    pub_path = metadata_dir / "public_key.pem"

    if not priv_path.exists():
        print("🔑 Gerando par de chaves criptográficas RSA...")
        # Gera chave privada
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        
        # Salva chave privada
        with open(priv_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        
        # Salva chave pública correspondente
        public_key = private_key.public_key()
        with open(pub_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )
        print("✅ Chaves RSA criadas com sucesso.")
    else:
        print("🔑 Chaves RSA já existentes.")


def seal():
    root = get_project_root()
    metadata_dir = root / "src" / "backend" / "core" / "metadata"
    os.makedirs(metadata_dir, exist_ok=True)

    # 1. Garante a existência das chaves
    generate_keys(metadata_dir)

    priv_path = metadata_dir / "private_key.pem"
    if not priv_path.exists():
        print("🚨 ERRO CRÍTICO: Chave privada não encontrada. O selamento do projeto deve ser feito no 'berço'.")
        sys.exit(1)

    # 2. Varre os arquivos críticos para compor o Manifesto
    print("📂 Fazendo varredura dos arquivos Python...")
    files_to_sign = []
    
    # Arquivos críticos da raiz
    for fname in ["v8_security_gate.py", "v8_sentinel.py", "init_env.py", "start_all.py"]:
        path = root / fname
        if path.exists():
            files_to_sign.append(path)

    # Todos os arquivos em src/backend/
    backend_dir = root / "src" / "backend"
    for r, d, f_list in os.walk(backend_dir):
        # Ignora metadados e cache
        if "metadata" in r or "__pycache__" in r:
            continue
        for f in f_list:
            if f.endswith(".py"):
                files_to_sign.append(pathlib.Path(r) / f)

    # 3. Gera o Manifesto de Hashes
    manifest = {}
    for fpath in files_to_sign:
        rel_path = fpath.relative_to(root).as_posix()
        manifest[rel_path] = get_file_sha256(fpath)

    # 4. Assina o Manifesto usando a Chave Privada
    print("✍️ Assinando o manifesto com a chave privada...")
    with open(priv_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    manifest_data = json.dumps(manifest, sort_keys=True).encode("utf-8")
    signature = private_key.sign(
        manifest_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # 5. Salva o Manifesto e a Assinatura em signature.json
    payload = {
        "manifest": manifest,
        "signature_hex": signature.hex()
    }

    sig_file_path = metadata_dir / "signature.json"
    with open(sig_file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, sort_keys=True)

    print(f"🔒 Projeto selado com sucesso! Manifesto salvo em: {sig_file_path}")


if __name__ == "__main__":
    seal()
