import { useState } from "react";
import { api } from "../../shared/api";
import toast from "react-hot-toast";
import Seo from "../../shared/Seo";

export default function CreateMeeting() {
  const role = localStorage.getItem("role");

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState("");

  // если не админ — показываем 403
  if (role !== "admin") {
    return <div>403: Недостаточно прав для создания встречи</div>;
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // datetime-local обычно отдаёт "YYYY-MM-DDTHH:MM"
      // приводим к "YYYY-MM-DDTHH:MM:00"
      const meetingDate = date.length === 16 ? `${date}:00` : date;

      await api.post("/meetings/", {
        title,
        description: description.trim() === "" ? null : description,
        meeting_date: meetingDate,
      });

      toast.success("Встреча создана");
      setTitle("");
      setDescription("");
      setDate("");
    } catch {
      toast.error("Ошибка при создании");
    }
  };

  return (
    <>
    <Seo
      title="Создание встречи — Whisper Mood"
      description="Создание новой встречи в приложении Whisper Mood."
      canonical="/meetings/new"
      noindex
    />
    <form onSubmit={submit} className="card">
      <h2>Новая встреча</h2>

      <input
        placeholder="Название"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      <textarea
        placeholder="Описание"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <input
        type="datetime-local"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        required
      />

      <button>Создать</button>
    </form>
    </>
  );
}