import "./Home.css";

import Hero from "../components/Hero";
import ActionButton from "../components/ActionButton";
import FeatureCard from "../components/FeatureCard";
import InfoSection from "../components/InfoSection";

import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";


function Home() {
  const navigate = useNavigate();
  const { t } = useLanguage();


  return (
    <>

      <Hero />


      <div className="buttons">

        <ActionButton
          text={t.home.ask}
          color="#2563EB"
          onClick={() =>
            navigate("/chat")
          }
        />


        <ActionButton
          text={t.home.upload}
          color="#16A34A"
          onClick={() =>
            navigate("/upload")
          }
        />


        <ActionButton
          text={t.home.complaint}
          color="#DC2626"
          onClick={() =>
            navigate("/complaint")
          }
        />

        <ActionButton
          text={t.home.assess}
          color="#7C3AED"
          onClick={() =>
            navigate("/case-assessment")
          }
        />

      </div>


      <InfoSection />


      <section className="features">

        <FeatureCard
          title={t.home.chatTitle}
          description={t.home.chatDesc}
        />


        <FeatureCard
          title={t.home.docTitle}
          description={t.home.docDesc}
        />


        <FeatureCard
          title={t.home.complaintTitle}
          description={t.home.complaintDesc}
        />

        <FeatureCard
          title={t.home.caseTitle}
          description={t.home.caseDesc}
        />

      </section>

    </>
  );
}


export default Home;