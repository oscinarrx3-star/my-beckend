def generate_suggestions(nlp_result: dict, scores: dict) -> dict:
    """Analiz sonuçlarına göre iyileştirme önerileri üretir."""
    suggestions = {
        "critical": [],    # Kritik - hemen düzelt
        "important": [],   # Önemli - düzeltilmeli
        "nice_to_have": [],  # İyi olur - bonus
    }

    # --- Kritik öneriler ---
    contact = nlp_result.get("contact_info", {})
    if not contact.get("email"):
        suggestions["critical"].append("CV'nize e-posta adresinizi eklemelisiniz.")
    if not contact.get("phone"):
        suggestions["critical"].append("CV'nize telefon numaranızı eklemelisiniz.")

    missing = nlp_result.get("missing_sections", [])
    if "deneyim" in missing:
        suggestions["critical"].append("'İş Deneyimi' bölümü eksik. ATS sistemleri bu bölümü arar.")
    if "eğitim" in missing:
        suggestions["critical"].append("'Eğitim' bölümü eksik. Mutlaka ekleyin.")
    if "beceriler" in missing:
        suggestions["critical"].append("'Beceriler' bölümü eksik. Teknik becerilerinizi listeleyin.")

    # --- Önemli öneriler ---
    if scores.get("keyword_score", 0) < 50:
        suggestions["important"].append(
            "Anahtar kelime yoğunluğu düşük. İlan metnindeki anahtar kelimeleri CV'nize ekleyin."
        )

    verbs = nlp_result.get("action_verbs_used", [])
    if len(verbs) < 3:
        suggestions["important"].append(
            "Daha fazla aksiyon fiili kullanın: 'Geliştirdim', 'Yönettim', 'Optimize ettim', 'Tasarladım'."
        )

    achievements = nlp_result.get("quantifiable_achievements", [])
    if len(achievements) < 2:
        suggestions["important"].append(
            "Sayısal başarılar ekleyin: '%20 verimlilik artışı', '50+ müşteri', '₺1M bütçe yönetimi'."
        )

    if not contact.get("linkedin"):
        suggestions["important"].append("LinkedIn profil linkinizi ekleyin.")

    # --- Nice to have ---
    if scores.get("format_score", 0) < 70:
        suggestions["nice_to_have"].append(
            "CV formatınızı düzenleyin. Standart bölüm başlıkları ve tutarlı tarih formatı kullanın."
        )

    format_issues = nlp_result.get("format_issues", [])
    for issue in format_issues[:3]:
        suggestions["nice_to_have"].append(f"Format sorunu: {issue}")

    if "projeler" in missing:
        suggestions["nice_to_have"].append("'Projeler' bölümü ekleyerek deneyiminizi destekleyin.")

    if "sertifikalar" in missing:
        suggestions["nice_to_have"].append("Varsa sertifikalarınızı ekleyin.")

    return suggestions
