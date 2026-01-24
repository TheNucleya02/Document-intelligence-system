import { Navigate } from "react-router-dom";

export default function Dashboard() {
  // Redirect to documents page by default
  return <Navigate to="/dashboard/documents" replace />;
}
