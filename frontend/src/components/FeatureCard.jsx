import "./FeatureCard.css";

function FeatureCard({ title, description, icon = "⚖", accent = "gold" }) {
  return (
    <article className={`feature-card feature-${accent}`}>
      <div className="feature-icon" aria-hidden="true">{icon}</div>
      <div className="feature-card-copy">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </article>
  );
}

export default FeatureCard;
