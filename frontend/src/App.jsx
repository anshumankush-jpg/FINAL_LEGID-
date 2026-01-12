import React, { useState, useEffect } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import OnboardingWizard from './components/OnboardingWizard'
import LawTypeSelector from './components/LawTypeSelector'

function App() {
  const [preferences, setPreferences] = useState(null);
  const [lawTypeSelection, setLawTypeSelection] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [showLawSelector, setShowLawSelector] = useState(false);

  useEffect(() => {
    // Check if preferences exist in localStorage
    const savedPreferences = localStorage.getItem('plaza_ai_preferences');
    const savedLawType = localStorage.getItem('plaza_ai_law_type');
    
    if (savedPreferences) {
      try {
        const prefs = JSON.parse(savedPreferences);
        setPreferences(prefs);
        setShowOnboarding(false);
        
        // Check if law type is saved
        if (savedLawType) {
          const lawType = JSON.parse(savedLawType);
          setLawTypeSelection(lawType);
          setShowLawSelector(false);
        } else {
          setShowLawSelector(true);
        }
      } catch (error) {
        console.error('Error loading preferences:', error);
        setShowOnboarding(true);
      }
    }
  }, []);

  const handleOnboardingComplete = (prefs) => {
    setPreferences(prefs);
    setShowOnboarding(false);
    setShowLawSelector(true); // Go directly to law selector after onboarding
  };


  const handleLawTypeComplete = (lawType) => {
    setLawTypeSelection(lawType);
    localStorage.setItem('plaza_ai_law_type', JSON.stringify(lawType));
    setShowLawSelector(false);
  };

  const handleResetPreferences = () => {
    localStorage.removeItem('plaza_ai_preferences');
    localStorage.removeItem('plaza_ai_law_type');
    setPreferences(null);
    setLawTypeSelection(null);
    setShowOnboarding(true);
    setShowLawSelector(false);
  };

  const handleChangeLawType = () => {
    localStorage.removeItem('plaza_ai_law_type');
    setLawTypeSelection(null);
    setShowLawSelector(true);
  };

  const handleBackToSettings = () => {
    localStorage.removeItem('plaza_ai_preferences');
    localStorage.removeItem('plaza_ai_law_type');
    setPreferences(null);
    setLawTypeSelection(null);
    setShowOnboarding(true);
    setShowLawSelector(false);
  };

  // Show onboarding first
  if (showOnboarding) {
    return <OnboardingWizard onComplete={handleOnboardingComplete} />;
  }

  // Then show law type selector
  if (showLawSelector || !lawTypeSelection) {
    return <LawTypeSelector 
      preferences={preferences} 
      onComplete={handleLawTypeComplete}
      onBack={handleBackToSettings}
    />;
  }

  // Finally show chat interface with welcome message
  return (
    <ChatInterface 
      preferences={preferences}
      lawTypeSelection={lawTypeSelection}
      onResetPreferences={handleResetPreferences}
      onChangeLawType={handleChangeLawType}
    />
  );
}

export default App
