#!/usr/bin/env python
"""
Backend deployment setup script.
Kullanım: python scripts/deploy.py
"""
import subprocess
import sys
import os


def run(cmd, description):
    """Command çalıştır ve sonuç göster."""
    print(f"\n🔄 {description}")
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"✓ {description} başarı ile tamamlandı")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} başarısız: {e}")
        return False


def deploy():
    """Deployment script'i çalıştır."""
    steps = [
        ("python -m pip install --upgrade pip", "Pip'i güncelle"),
        ("pip install -r requirements.txt", "Bağımlılıkları yükle"),
        ("python scripts/setup_nlp.py", "NLP modellerini indir"),
        ("python -m alembic upgrade head", "Database migration'larını çalıştır"),
        ("python -m pytest -q", "Testleri çalıştır"),
    ]
    
    print("=" * 50)
    print("Backend Deployment Setup")
    print("=" * 50)
    
    results = []
    for cmd, desc in steps:
        success = run(cmd, desc)
        results.append((desc, success))
        if not success:
            print(f"\n⚠ {desc} başarısız oldu. Devam etmek için enter'a bas...")
            input()
    
    print("\n" + "=" * 50)
    print("Deployment Özeti")
    print("=" * 50)
    
    for desc, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {desc}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print("\n✓ Deployment başarılı!")
        print("\nSunucuyu başlatmak için:")
        print("  uvicorn app.main:app --reload --port 8000")
    else:
        print("\n✗ Bazı adımlar başarısız oldu. Yukarıdaki hataları kontrol et.")
        sys.exit(1)


if __name__ == "__main__":
    deploy()
