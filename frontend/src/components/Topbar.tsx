import { Link, useNavigate } from "react-router-dom";
import {
  FaBookOpen,
  FaPen,
  FaComments,
  FaCalendarAlt,
  FaUser,
  FaSignOutAlt,
} from "react-icons/fa";
import { api } from "../shared/api";

export default function Topbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");

      if (refreshToken) {
        await api.post("/auth/logout", {
          refresh_token: refreshToken,
        });
      }
    } catch (e) {
      console.error("Logout error:", e);
    } finally {
      localStorage.clear();
      navigate("/login");
    }
  };

  return (
    <header className="topbar">
      <Link className="brand" to="/">Whisper Mood</Link>

      <nav>
        {token ? (
          <>
            <Link to="/entries/new">
              <FaPen style={{ marginRight: 6 }} />
              Запись
            </Link>

            <Link to="/entries">
              <FaBookOpen style={{ marginRight: 6 }} />
              Мои записи
            </Link>

            <Link to="/rooms">
              <FaComments style={{ marginRight: 6 }} />
              Комнаты
            </Link>

            <Link to="/meetings">
              <FaCalendarAlt style={{ marginRight: 6 }} />
              Встречи
            </Link>

            <button onClick={logout} className="link-like">
              <FaSignOutAlt style={{ marginRight: 6 }} />
              Выйти
            </button>
          </>
        ) : (
          <Link to="/login">
            <FaUser style={{ marginRight: 6 }} />
            Войти
          </Link>
        )}
      </nav>
    </header>
  );
}