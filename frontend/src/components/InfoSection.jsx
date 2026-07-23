import "./InfoSection.css";

function InfoSection() {
  return (
    <section className="info-section">

      <h2>🌍 Multilingual Legal Assistance</h2>

      <p>
        LawMate AI supports multiple Indian languages,
        making legal guidance accessible to everyone.
      </p>

      <div className="languages">

        <span>🇬🇧 English</span>

        <span>🇮🇳 हिन्दी</span>

        <span>🇮🇳 ಕನ್ನಡ</span>

        <span>🇮🇳 தமிழ்</span>

        <span>🇮🇳 తెలుగు</span>

        <span>🇮🇳 മലയാളം</span>

      </div>

    </section>
  );
}

export default InfoSection;