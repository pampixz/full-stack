import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../../shared/api";
import Seo from "../../shared/Seo";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
  
    try {
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);
  
      const res = await api.post("/auth/login", form, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
  
      // сохраняем токены
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
  
      // получаем пользователя
      const me = await api.get("/auth/me");
  
      localStorage.setItem("role", me.data.role);
  
      navigate("/entries");
  
    } catch (err) {
      console.log(err);
      setError("Неверный email или пароль");
    }
  };

  return (
    <>
      <Seo
        title="Вход — Whisper Mood"
        description="Страница входа в личный кабинет Whisper Mood."
        canonical="/login"
        noindex
      />
  
      <section className="card" style={{ maxWidth: 420, margin: "0 auto" }}>
        <h2>Вход</h2>
  
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
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
  
          <button type="submit">Войти</button>
        </form>
  
        {error && <p className="muted">{error}</p>}
  
        <p style={{ marginTop: 12 }}>
          Нет аккаунта? <Link to="/register">Регистрация</Link>
        </p>
      </section>
    </>
  );
}