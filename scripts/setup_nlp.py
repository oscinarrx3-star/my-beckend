#!/usr/bin/env python
"""
NLP modelleriyi indir ve setup et.
Kullanım: python scripts/setup_nlp.py
"""
import subprocess
import sys


def setup_spacy_models():
    """Spacy Türkçe modeli indir."""
    print("🔄 Spacy Türkçe modeli indiriliyor...")
    try:
        # Türkçe model
        subprocess.check_call([
            sys.executable, "-m", "spacy", "download", "tr_core_news_trf"
        ])
        print("✓ Spacy Türkçe modeli başarıyla yüklendi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Spacy model kurulumu başarısız: {e}")
        return False


def setup_nltk_data():
    """NLTK veri dosyalarını indir (opsiyonel, fallback için)."""
    print("🔄 NLTK veri dosyaları indiriliyor...")
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
        print("✓ NLTK veri dosyaları başarıyla yüklendi")
        return True
    except Exception as e:
        print(f"⚠ NLTK kurulumu başarısız (opsiyonel): {e}")
        return False


def main():
    print("=" * 50)
    print("NLP Modelleri Setup Başlatılıyor")
    print("=" * 50)
    
    spacy_ok = setup_spacy_models()
    nltk_ok = setup_nltk_data()
    
    print("\n" + "=" * 50)
    if spacy_ok:
        print("✓ Setup başarılı! Backend hazır.")
    else:
        print("⚠ Bazı modeller kurulamadı. Fallback analiz kullanılacak.")
    print("=" * 50)


if __name__ == "__main__":
    main()
