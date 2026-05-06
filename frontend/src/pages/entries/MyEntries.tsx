import { useEffect, useState } from "react";
import { api } from "../../shared/api";
import {
  FaHashtag,
  FaTrash,
  FaEdit,
  FaSave,
  FaTimes,
  FaUpload,
  FaDownload,
  FaPaperclip,
} from "react-icons/fa";
import { useSearchParams } from "react-router-dom";
import Seo from "../../shared/Seo";

type Entry = {
  id: number;
  text: string;
  tags: string[];
  created_at: string;
};

type EntriesResponse = {
  items: Entry[];
  total: number;
  page: number;
  page_size: number;
};

type EntryFile = {
  id: number;
  entry_id: number;
  original_name: string;
  content_type: string;
  file_size: number;
  created_at: string;
};

export default function MyEntries() {
  const [searchParams, setSearchParams] = useSearchParams();

  const q = searchParams.get("q") || "";
  const tag = searchParams.get("tag") || "";
  const dateFrom = searchParams.get("date_from") || "";
  const dateTo = searchParams.get("date_to") || "";
  const sort = searchParams.get("sort") || "-created_at";
  const page = Number(searchParams.get("page") || "1");
  const pageSize = Number(searchParams.get("page_size") || "5");

  const [entries, setEntries] = useState<Entry[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const [qInput, setQInput] = useState(q);
  const [tagInput, setTagInput] = useState(tag);
  const [dateFromInput, setDateFromInput] = useState(dateFrom);
  const [dateToInput, setDateToInput] = useState(dateTo);
  const [sortInput, setSortInput] = useState(sort);

  const [editing, setEditing] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [editTags, setEditTags] = useState("");

  const [filesByEntry, setFilesByEntry] = useState<Record<number, EntryFile[]>>({});
  const [selectedFiles, setSelectedFiles] = useState<Record<number, File | null>>({});
  const [uploadingEntryId, setUploadingEntryId] = useState<number | null>(null);

  useEffect(() => {
    setQInput(q);
    setTagInput(tag);
    setDateFromInput(dateFrom);
    setDateToInput(dateTo);
    setSortInput(sort);
  }, [q, tag, dateFrom, dateTo, sort]);

  useEffect(() => {
    loadEntries();
  }, [q, tag, dateFrom, dateTo, sort, page, pageSize]);

  const loadEntries = async () => {
    try {
      const res = await api.get<EntriesResponse>("/entries/", {
        params: {
          q: q || undefined,
          tag: tag || undefined,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
          sort,
          page,
          page_size: pageSize,
        },
      });

      setEntries(res.data.items);
      setTotal(res.data.total);
      setError(null);

      // после загрузки записей загружаем файлы для каждой записи
      for (const entry of res.data.items) {
        loadFiles(entry.id);
      }
    } catch (err) {
      console.error(err);
      setError("Ошибка загрузки данных 😔");
    }
  };

  const loadFiles = async (entryId: number) => {
    try {
      const res = await api.get<EntryFile[]>(`/entry-files/${entryId}`);
      setFilesByEntry((prev) => ({
        ...prev,
        [entryId]: res.data,
      }));
    } catch (err) {
      console.error(`Ошибка загрузки файлов для записи ${entryId}`, err);
    }
  };

  const applyFilters = () => {
    const params = new URLSearchParams();

    if (qInput.trim()) params.set("q", qInput.trim());
    if (tagInput.trim()) params.set("tag", tagInput.trim());
    if (dateFromInput) params.set("date_from", dateFromInput);
    if (dateToInput) params.set("date_to", dateToInput);
    if (sortInput) params.set("sort", sortInput);

    params.set("page", "1");
    params.set("page_size", String(pageSize));

    setSearchParams(params);
  };

  const resetFilters = () => {
    setQInput("");
    setTagInput("");
    setDateFromInput("");
    setDateToInput("");
    setSortInput("-created_at");

    setSearchParams({
      page: "1",
      page_size: String(pageSize),
      sort: "-created_at",
    });
  };

  const handlePageChange = (newPage: number) => {
    const params = new URLSearchParams(searchParams);
    params.set("page", String(newPage));
    setSearchParams(params);
  };

  const handlePageSizeChange = (newSize: number) => {
    const params = new URLSearchParams(searchParams);
    params.set("page_size", String(newSize));
    params.set("page", "1");
    setSearchParams(params);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Удалить запись?")) return;

    try {
      await api.delete(`/entries/${id}`);
      loadEntries();
    } catch (err) {
      alert("Ошибка при удалении 😔");
    }
  };

  const startEdit = (entry: Entry) => {
    setEditing(entry.id);
    setEditText(entry.text);
    setEditTags(entry.tags.join(", "));
  };

  const cancelEdit = () => {
    setEditing(null);
    setEditText("");
    setEditTags("");
  };

  const saveEdit = async (id: number) => {
    try {
      await api.put(`/entries/${id}`, {
        text: editText,
        tags: editTags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      });

      setEditing(null);
      setEditText("");
      setEditTags("");
      loadEntries();
    } catch (err) {
      alert("Ошибка при сохранении изменений 😔");
    }
  };

  const handleFileSelect = (entryId: number, file: File | null) => {
    setSelectedFiles((prev) => ({
      ...prev,
      [entryId]: file,
    }));
  };

  const uploadFile = async (entryId: number) => {
    const file = selectedFiles[entryId];

    if (!file) {
      alert("Сначала выберите файл");
      return;
    }

    try {
      setUploadingEntryId(entryId);

      const formData = new FormData();
      formData.append("uploaded_file", file);

      await api.post(`/entry-files/${entryId}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setSelectedFiles((prev) => ({
        ...prev,
        [entryId]: null,
      }));

      await loadFiles(entryId);
      alert("Файл успешно загружен");
    } catch (err: any) {
      console.error(err);
      alert(
        err?.response?.data?.detail || "Ошибка при загрузке файла"
      );
    } finally {
      setUploadingEntryId(null);
    }
  };

  const downloadFile = async (fileId: number, fileName: string) => {
    try {
      const res = await api.get(`/entry-files/download/${fileId}`, {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      alert("Ошибка при скачивании файла");
    }
  };

  const deleteFile = async (entryId: number, fileId: number) => {
    if (!confirm("Удалить файл?")) return;

    try {
      await api.delete(`/entry-files/${fileId}`);
      await loadFiles(entryId);
    } catch (err) {
      console.error(err);
      alert("Ошибка при удалении файла");
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <section>
      <Seo
        title="Мои записи — Whisper Mood"
        description="Личный раздел записей пользователя в приложении Whisper Mood."
        canonical="/entries"
        noindex
      />

      <h2>Мои записи</h2>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>Фильтры</h3>

        <input
          placeholder="Поиск по тексту"
          value={qInput}
          onChange={(e) => setQInput(e.target.value)}
        />

        <input
          placeholder="Фильтр по тегу"
          value={tagInput}
          onChange={(e) => setTagInput(e.target.value)}
        />

        <div className="row" style={{ gap: 12, marginTop: 10 }}>
          <div style={{ flex: 1 }}>
            <label>Дата от</label>
            <input
              type="datetime-local"
              value={dateFromInput}
              onChange={(e) => setDateFromInput(e.target.value)}
            />
          </div>

          <div style={{ flex: 1 }}>
            <label>Дата до</label>
            <input
              type="datetime-local"
              value={dateToInput}
              onChange={(e) => setDateToInput(e.target.value)}
            />
          </div>
          </div>

<div style={{ marginTop: 10 }}>
  <label>Сортировка</label>
  <select
    value={sortInput}
    onChange={(e) => setSortInput(e.target.value)}
  >
    <option value="-created_at">Сначала новые</option>
    <option value="created_at">Сначала старые</option>
    <option value="text">Текст А-Я</option>
    <option value="-text">Текст Я-А</option>
  </select>
</div>

<div className="row" style={{ marginTop: 12, gap: 10 }}>
  <button type="button" onClick={applyFilters}>
    Применить
  </button>
  <button type="button" onClick={resetFilters}>
    Сбросить
  </button>
</div>
</div>

<div className="row" style={{ marginBottom: 16, gap: 10 }}>
<div className="muted">
  Всего записей: <strong>{total}</strong>
</div>

<div>
  <label>На странице: </label>
  <select
    value={pageSize}
    onChange={(e) => handlePageSizeChange(Number(e.target.value))}
  >
    <option value={5}>5</option>
    <option value={10}>10</option>
    <option value={20}>20</option>
  </select>
</div>
</div>

{error && <p className="muted">{error}</p>}

<ul className="list">
{entries.map((e) => (
  <li key={e.id} className="card">
    <div className="muted">
      {new Date(e.created_at).toLocaleString()}
    </div>

    {editing === e.id ? (
      <>
        <textarea
          value={editText}
          onChange={(ev) => setEditText(ev.target.value)}
          rows={4}
        />

        <input
          value={editTags}
          onChange={(ev) => setEditTags(ev.target.value)}
          placeholder="теги через запятую"
        />

        <div className="row" style={{ marginTop: 10 }}>
          <button type="button" onClick={() => saveEdit(e.id)}>
            <FaSave style={{ marginRight: 6 }} />
            Сохранить
          </button>

          <button type="button" onClick={cancelEdit}>
            <FaTimes style={{ marginRight: 6 }} />
            Отмена
          </button>
        </div>
      </>
    ) : (
      <>
        <p>{e.text}</p>

        <div className="tags">
          {e.tags.map((t) => (
            <span key={t} className="tag">
              <FaHashtag style={{ marginRight: 4, opacity: 0.7 }} />
              {t}
            </span>
          ))}
        </div>

        <div className="row" style={{ marginTop: 10 }}>
          <button type="button" onClick={() => startEdit(e)}>
            <FaEdit style={{ marginRight: 6 }} />
            Изменить
          </button>

          <button
            type="button"
            onClick={() => handleDelete(e.id)}
            style={{
              background: "#f6d0d0",
              border: "1px solid #e9b8b8",
            }}
          >
            <FaTrash style={{ marginRight: 6 }} />
            Удалить
          </button>
        </div>

        <div className="card" style={{ marginTop: 16 }}>
          <h4 style={{ marginTop: 0 }}>
            <FaPaperclip style={{ marginRight: 6 }} />
            Прикреплённые файлы
          </h4>

          <input
            type="file"
            onChange={(ev) =>
              handleFileSelect(e.id, ev.target.files?.[0] || null)
            }
          />

          <button
            type="button"
            onClick={() => uploadFile(e.id)}
            disabled={uploadingEntryId === e.id}
                    style={{ marginTop: 10 }}
                  >
                    <FaUpload style={{ marginRight: 6 }} />
                    {uploadingEntryId === e.id ? "Загрузка..." : "Загрузить файл"}
                  </button>

                  <ul style={{ marginTop: 12 }}>
                    {(filesByEntry[e.id] || []).map((file) => (
                      <li key={file.id} style={{ marginBottom: 8 }}>
                        <strong>{file.original_name}</strong>{" "}
                        <span className="muted">
                          ({Math.round(file.file_size / 1024)} КБ)
                        </span>

                        <div className="row" style={{ marginTop: 6 }}>
                          <button
                            type="button"
                            onClick={() => downloadFile(file.id, file.original_name)}
                          >
                            <FaDownload style={{ marginRight: 6 }} />
                            Скачать
                          </button>

                          <button
                            type="button"
                            onClick={() => deleteFile(e.id, file.id)}
                            style={{
                              background: "#f6d0d0",
                              border: "1px solid #e9b8b8",
                            }}
                          >
                            <FaTrash style={{ marginRight: 6 }} />
                            Удалить файл
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>

                  {(filesByEntry[e.id] || []).length === 0 && (
                    <p className="muted">Файлов пока нет</p>
                  )}
                </div>
              </>
            )}
          </li>
        ))}

        {entries.length === 0 && (
          <li className="muted">Ничего не найдено…</li>
        )}
      </ul>

      <div className="row" style={{ marginTop: 16, gap: 10 }}>
        <button
          type="button"
          onClick={() => handlePageChange(page - 1)}
          disabled={page <= 1}
        >
          Назад
        </button>

        <span>
          Страница <strong>{page}</strong> из <strong>{totalPages}</strong>
        </span>

        <button
          type="button"
          onClick={() => handlePageChange(page + 1)}
          disabled={page >= totalPages}
        >
          Вперёд
        </button>
      </div>
    </section>
  );
}