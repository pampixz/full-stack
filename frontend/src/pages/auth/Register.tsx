import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../../shared/api";
import Seo from "../../shared/Seo";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      // Регистрация
      await api.post("/auth/register", {
        email,
        password,
      });

      // Логин сразу после регистрации
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);

      const res = await api.post("/auth/login", form, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      // Сохраняем токены
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);

      // Получаем роль
      const me = await api.get("/auth/me");
      localStorage.setItem("role", me.data.role);

      navigate("/entries");

    } catch (err: any) {
      console.log(err);

      if (err?.response?.status === 400) {
        setError("Этот email уже зарегистрирован");
      } else {
        setError("Ошибка регистрации");
      }
    }
  };

  return (
    <>
      <Seo
        title="Регистрация — Whisper Mood"
        description="Создание аккаунта в приложении Whisper Mood."
        canonical="/register"
        noindex
      />

      <section className="card" style={{ maxWidth: 420, margin: "0 auto" }}>
        <h2>Регистрация</h2>

        <form onSubmit={submit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Пароль (мин. 6 символов)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={6}
            required
          />

          <button type="submit">Создать аккаунт</button>
        </form>

        {error && <p className="muted">{error}</p>}

        <p style={{ marginTop: 12 }}>
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </section>
    </>
  );
}