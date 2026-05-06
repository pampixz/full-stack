import { Navigate, Outlet } from "react-router-dom";

type Props = {
  roles?: string[];
};

export default function ProtectedRoute({ roles }: Props) {
  const token = localStorage.getItem("access_token"); 
  const role = localStorage.getItem("role");

  if (!token) return <Navigate to="/login" replace />;

  if (roles && role && !roles.includes(role)) {
    return <div>403: недостаточно прав</div>;
  }

  return <Outlet />;
}