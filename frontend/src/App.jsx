import { useAuth } from "./auth/useAuth";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";

function App() {
  const { token, login } = useAuth();

  if (!token) {
    return <AuthPage onLogin={login} />;
  }

  return <Dashboard />;
}

export default App;