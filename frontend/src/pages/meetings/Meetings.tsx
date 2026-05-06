import { useEffect, useState } from "react";
import { api } from "../../shared/api";
import Seo from "../../shared/Seo";

type Meeting = {
  id: number;
  title: string;
  description: string;
  meeting_date: string;
};

export default function Meetings() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [showForm, setShowForm] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState("");

  const role = localStorage.getItem("role");
  const isAdmin = role === "admin";

  useEffect(() => {
    loadMeetings();
  }, []);

  const loadMeetings = async () => {
    try {
      const res = await api.get("/meetings/");
      setMeetings(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const createMeeting = async () => {
    try {
      // проверяем формат из input datetime-local
      const validDatePattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/;
  
      if (!validDatePattern.test(date)) {
        alert("Введите корректную дату и время");
        return;
      }
  
      const meetingDate = `${date}:00`;
  
      await api.post("/meetings/", {
        title,
        description: description.trim() === "" ? null : description,
        meeting_date: meetingDate,
      });
  
      setTitle("");
      setDescription("");
      setDate("");
      setShowForm(false);
      loadMeetings();
    } catch (e) {
      console.error("CREATE MEETING ERROR:", e);
      alert("Ошибка при создании встречи");
    }
  };

  const deleteMeeting = async (id: number) => {
    if (!confirm("Удалить встречу?")) return;

    try {
      await api.delete(`/meetings/${id}`);
      setMeetings(meetings.filter((m) => m.id !== id));
    } catch (e) {
      alert("Ошибка при удалении встречи 😔");
    }
  };

  return (
    <section>
      <Seo
  title="Встречи — Whisper Mood"
  description="Список встреч в приложении Whisper Mood."
  canonical="/meetings"
  noindex
      />
      <h2>Встречи</h2>

      {isAdmin && (
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Отмена" : "Создать встречу"}
        </button>
      )}

      {isAdmin && showForm && (
        <div className="card">
          <input
            placeholder="Название встречи"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
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
          />

          <button onClick={createMeeting}>Сохранить</button>
        </div>
      )}

      {meetings.length === 0 && <p>Встреч пока нет</p>}

      <ul className="list">
        {meetings.map((m) => (
          <li key={m.id} className="card">
            <h3>{m.title}</h3>
            <p>{m.description}</p>

            <div className="muted">
              {new Date(m.meeting_date).toLocaleString()}
            </div>

            {isAdmin && (
              <button
                onClick={() => deleteMeeting(m.id)}
                style={{
                  marginTop: 10,
                  background: "#f6d0d0",
                  border: "1px solid #e9b8b8",
                }}
              >
                Удалить
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}