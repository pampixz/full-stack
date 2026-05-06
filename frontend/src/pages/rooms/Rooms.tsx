import Seo from "../../shared/Seo";
export default function Rooms() {
  const rooms = [
    {
      id: 1,
      title: "Анонимная поддержка",
      description: "Чат поддержки с ботом в Telegram",
      link: "https://t.me/whisper_mood_bot",
    },
    {
      id: 2,
      title: "Тревога и стресс",
      description: "Обсуждение тревожных состояний",
      link: "https://t.me/whisper_mood_bot",
    },
    {
      id: 3,
      title: "Просто поговорить",
      description: "Свободное общение",
      link: "https://t.me/whisper_mood_bot",
    },
  ];

  return (
    <section>
      <Seo
        title="Комнаты поддержки — Whisper Mood"
        description="Раздел комнат поддержки в приложении Whisper Mood."
        canonical="/rooms"
        noindex
      />
      <h2>Комнаты</h2>

      <ul className="list">
        {rooms.map((r) => (
          <li key={r.id} className="card">
            <h3>{r.title}</h3>
            <p>{r.description}</p>

            <a
              href={r.link}
              target="_blank"
              rel="noopener noreferrer"
              className="btn"
            >
              Подключиться
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}