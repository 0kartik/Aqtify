import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import MarketingLayout from "./layouts/MarketingLayout.jsx";
import StandalonePage from "./layouts/StandalonePage.jsx";
import LandingPage from "./pages/LandingPage.jsx";
import HowItWorksPage from "./pages/HowItWorksPage.jsx";
import ConsoleIndexPage from "./pages/ConsoleIndexPage.jsx";

import RegisterPanel from "./panels/RegisterPanel.jsx";
import BulkRegisterPanel from "./panels/BulkRegisterPanel.jsx";
import VerifyPanel from "./panels/VerifyPanel.jsx";
import PublicVerifyPanel from "./panels/PublicVerifyPanel.jsx";
import HistoryPanel from "./panels/HistoryPanel.jsx";
import ReviewQueuePanel from "./panels/ReviewQueuePanel.jsx";

import { API_DEFAULT } from "./api/client.js";

export default function App() {
  const [apiKey, setApiKey] = useState(localStorage.getItem("aqtify_api_key") || "");
  const apiBase = API_DEFAULT;

  return (
    <BrowserRouter>
      <Routes>
        {/* Marketing site */}
        <Route
          path="/"
          element={
            <MarketingLayout>
              <LandingPage />
            </MarketingLayout>
          }
        />
        <Route
          path="/how-it-works"
          element={
            <MarketingLayout>
              <HowItWorksPage />
            </MarketingLayout>
          }
        />

        {/* Console index — the only place that lists all tools */}
        <Route path="/app" element={<ConsoleIndexPage />} />

        {/* Each tool is a fully standalone page: no shared nav, just this panel */}
        <Route
          path="/app/register"
          element={
            <StandalonePage title="Register" apiKey={apiKey} setApiKey={setApiKey}>
              <RegisterPanel apiBase={apiBase} apiKey={apiKey} />
            </StandalonePage>
          }
        />
        <Route
          path="/app/bulk"
          element={
            <StandalonePage title="Bulk register" apiKey={apiKey} setApiKey={setApiKey}>
              <BulkRegisterPanel apiBase={apiBase} apiKey={apiKey} />
            </StandalonePage>
          }
        />
        <Route
          path="/app/verify"
          element={
            <StandalonePage title="Verify" apiKey={apiKey} setApiKey={setApiKey}>
              <VerifyPanel apiBase={apiBase} apiKey={apiKey} />
            </StandalonePage>
          }
        />
        <Route
          path="/app/public-verify"
          element={
            <StandalonePage title="Public verify" apiKey={apiKey} setApiKey={setApiKey}>
              <PublicVerifyPanel apiBase={apiBase} />
            </StandalonePage>
          }
        />
        <Route
          path="/app/history"
          element={
            <StandalonePage title="History" apiKey={apiKey} setApiKey={setApiKey}>
              <HistoryPanel apiBase={apiBase} apiKey={apiKey} />
            </StandalonePage>
          }
        />
        <Route
          path="/app/review"
          element={
            <StandalonePage title="Review queue" apiKey={apiKey} setApiKey={setApiKey}>
              <ReviewQueuePanel apiBase={apiBase} apiKey={apiKey} />
            </StandalonePage>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}