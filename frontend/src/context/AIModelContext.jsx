import {
  createContext,
  useContext,
  useMemo,
  useState,
} from "react";

const AIModelContext = createContext(null);

const STORAGE_KEY = "lawmate-ai-mode";

export const aiModelOptions = [
  {
    value: "auto",
    label: "Auto (Recommended)",
    shortLabel: "Auto",
    description:
      "Uses Gemini when online and automatically switches to Local Llama when needed.",
  },
  {
    value: "gemini",
    label: "Gemini - Online",
    shortLabel: "Gemini",
    description:
      "Online AI mode using Google Gemini.",
  },
  {
    value: "llama",
    label: "Llama 3.2 3B - Local",
    shortLabel: "Local Llama",
    description:
      "Local AI mode that can work without internet.",
  },
];

const VALID_MODES = new Set(
  aiModelOptions.map((option) => option.value)
);

function getInitialMode() {
  if (typeof window === "undefined") {
    return "auto";
  }

  const savedMode = window.localStorage.getItem(
    STORAGE_KEY
  );

  return VALID_MODES.has(savedMode)
    ? savedMode
    : "auto";
}

export function AIModelProvider({ children }) {
  const [aiMode, setAiModeState] = useState(
    getInitialMode
  );

  const setAiMode = (mode) => {
    const nextMode = VALID_MODES.has(mode)
      ? mode
      : "auto";

    setAiModeState(nextMode);

    if (typeof window !== "undefined") {
      window.localStorage.setItem(
        STORAGE_KEY,
        nextMode
      );
    }
  };

  const activeModel = useMemo(
    () =>
      aiModelOptions.find(
        (option) => option.value === aiMode
      ) || aiModelOptions[0],
    [aiMode]
  );

  const value = useMemo(
    () => ({
      aiMode,
      setAiMode,
      activeModel,
      aiModelOptions,
    }),
    [aiMode, activeModel]
  );

  return (
    <AIModelContext.Provider value={value}>
      {children}
    </AIModelContext.Provider>
  );
}

export function useAIModel() {
  const context = useContext(
    AIModelContext
  );

  if (!context) {
    throw new Error(
      "useAIModel must be used inside AIModelProvider."
    );
  }

  return context;
}
