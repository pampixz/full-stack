import { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Topbar from "./components/Topbar";
import ProtectedRoute from "./routes/ProtectedRoute";

const Home = lazy(() => import("./pages/Home"));
const Login = lazy(() => import("./pages/auth/Login"));
const Register = lazy(() => import("./pages/auth/Register"));
const CreateEntry = lazy(() => import("./pages/entries/CreateEntry"));
const MyEntries = lazy(() => import("./pages/entries/MyEntries"));
const Rooms = lazy(() => import("./pages/rooms/Rooms"));
const Meetings = lazy(() => import("./pages/meetings/Meetings"));
const CreateMeeting = lazy(() => import("./pages/meetings/CreateMeeting"));

export default function App() {
  return (
    <div className="app">
      <Topbar />
      <main className="container">
        <Suspense fallback={<div>Загрузка страницы...</div>}>
          <Routes>
            <Route path="/" element={<Home />} />

            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route element={<ProtectedRoute roles={["user", "admin"]} />}>
              <Route path="/entries" element={<MyEntries />} />
              <Route path="/entries/new" element={<CreateEntry />} />
              <Route path="/rooms" element={<Rooms />} />
              <Route path="/meetings" element={<Meetings />} />
            </Route>

            <Route element={<ProtectedRoute roles={["admin"]} />}>
              <Route path="/meetings/new" element={<CreateMeeting />} />
            </Route>

            <Route path="/home" element={<Navigate to="/" replace />} />
            <Route path="*" element={<div>Страница не найдена</div>} />
          </Routes>
        </Suspense>
      </main>
    </div>
  );
}