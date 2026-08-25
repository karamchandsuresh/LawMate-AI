import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./CaseAssessment.css";


function CaseAssessment() {
  const [formData, setFormData] = useState({
    case_type: "consumer",
    case_facts: "",
    user_role: "",
    opposite_party: "",
    evidence_summary: "",
    desired_outcome: "",
  });

  const [assessment, setAssessment] = useState("");
  const [predictionNotice, setPredictionNotice] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");


  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
  };


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setAssessment("");
    setPredictionNotice("");

    if (
      formData.case_facts
        .trim()
        .length < 30
    ) {
      setError(
        "Please provide more detailed facts about the case."
      );

      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/assess-case",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(
            formData
          ),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Case assessment failed."
        );
      }

      setAssessment(
        data.assessment ||
        "Assessment completed, but no result was returned."
      );

      setPredictionNotice(
        data.prediction_notice || ""
      );

    } catch (err) {
      console.error(
        "Case assessment error:",
        err
      );

      setError(
        err.message ||
        "Something went wrong while assessing the case."
      );

    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="case-page">

      <h1>
        ⚖️ AI Case Assessment
      </h1>

      <p className="case-intro">
        Describe your legal situation and LawMate AI
        will provide a cautious qualitative assessment
        of the strengths, uncertainties, evidence needs,
        and possible next steps.
      </p>


      <div className="case-warning">
        ⚠️ LawMate does not predict or guarantee court
        outcomes. The assessment is based only on the
        information you provide.
      </div>


      <form
        className="case-form"
        onSubmit={handleSubmit}
      >

        <div className="case-form-section">

          <h2>
            Case Information
          </h2>


          <label>
            Case Type

            <select
              name="case_type"
              value={formData.case_type}
              onChange={handleChange}
            >
              <option value="consumer">
                Consumer
              </option>

              <option value="employment">
                Employment
              </option>

              <option value="property">
                Property
              </option>

              <option value="family">
                Family
              </option>

              <option value="cybercrime">
                Cybercrime
              </option>

              <option value="criminal">
                Criminal
              </option>

              <option value="civil">
                Civil
              </option>

              <option value="general">
                General
              </option>
            </select>
          </label>


          <div className="case-form-grid">

            <label>
              Your Role

              <input
                type="text"
                name="user_role"
                value={formData.user_role}
                onChange={handleChange}
                placeholder="Example: Consumer, Employee, Tenant"
              />
            </label>


            <label>
              Opposite Party

              <input
                type="text"
                name="opposite_party"
                value={formData.opposite_party}
                onChange={handleChange}
                placeholder="Person, company, employer, seller, etc."
              />
            </label>

          </div>


          <label>
            Case Facts
            <span className="case-required">
              *
            </span>

            <textarea
              name="case_facts"
              value={formData.case_facts}
              onChange={handleChange}
              placeholder="Explain what happened, including the important facts, sequence of events, dates if known, and what the other party did."
              rows="8"
              required
            />
          </label>


          <label>
            Evidence Summary

            <textarea
              name="evidence_summary"
              value={formData.evidence_summary}
              onChange={handleChange}
              placeholder="Example: Payment receipt, order confirmation, screenshots, emails, agreement, photographs..."
              rows="4"
            />
          </label>


          <label>
            Desired Outcome

            <textarea
              name="desired_outcome"
              value={formData.desired_outcome}
              onChange={handleChange}
              placeholder="Example: Full refund, unpaid salary, compensation, return of property..."
              rows="3"
            />
          </label>

        </div>


        {error && (
          <div className="case-error">
            ⚠️ {error}
          </div>
        )}


        <button
          type="submit"
          className="case-submit-button"
          disabled={isLoading}
        >
          {
            isLoading
              ? "Assessing Case..."
              : "Assess My Case"
          }
        </button>

      </form>


      {isLoading && (
        <div className="case-loading">

          <h3>
            ⚖️ Assessing your case...
          </h3>

          <p>
            LawMate AI is reviewing the facts,
            evidence summary, uncertainties,
            and possible next steps.
          </p>

        </div>
      )}


      {assessment && (
        <div className="case-result">

          <h2>
            📋 Case Assessment Result
          </h2>

          {predictionNotice && (
            <div className="case-prediction-notice">
              ⚠️ {predictionNotice}
            </div>
          )}

          <div className="case-result-content">
            <ReactMarkdown>
              {assessment}
            </ReactMarkdown>
          </div>

        </div>
      )}


      <div className="case-footer-note">
        LawMate AI provides general legal information
        and case-assessment assistance only. Actual legal
        outcomes depend on evidence, applicable law,
        procedure, arguments, authorities, and judicial
        interpretation.
      </div>

    </div>
  );
}


export default CaseAssessment;
