import { useState } from "react";
import { api } from "../../shared/api";
import toast from "react-hot-toast";
import Seo from "../../shared/Seo";

export default function CreateEntry() {
  const [text, setText] = useState("");
  const [tags, setTags] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const payload = {
        text,
        tags: tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      };

      await api.post("/entries/", payload);

      toast.success("Запись успешно сохранена!");
      setText("");
      setTags("");
    } catch (err) {
      console.error(err);
      toast.error("Ошибка при сохранении 😔");
    }
  };

  return (
    <>
      <Seo
        title="Новая запись — Whisper Mood"
        description="Создание новой записи в дневнике настроения."
        canonical="/entries/new"
        noindex
      />
    <form onSubmit={handleSubmit} className="card">
      <h2>Новая запись</h2>

      <textarea
        placeholder="Как ты сегодня?"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        required
      />

      <input
        placeholder="теги через запятую: тревога, радость"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />

      <button type="submit">Сохранить</button>
    </form>
    </>
  );
}