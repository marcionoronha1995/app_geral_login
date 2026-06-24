import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class V8SecurityException(Exception):
    """
    Exceção personalizada para falhas de validação de segurança do V8.
    """
    pass
