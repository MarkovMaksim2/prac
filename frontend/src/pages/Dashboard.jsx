import { useEffect, useState } from "react";
import api from "../api/client";
import Layout from "../layout/Layout";
import UploadModal from "../components/UploadModal";
import BatchModal from "../components/BatchModal";

export default function Dashboard() {
  const [batches, setBatches] = useState([]);
  const [selected, setSelected] = useState(null);
  const [openUpload, setOpenUpload] = useState(false);

  const load = async () => {
    const res = await api.get("/batches");
    setBatches(res.data);
  };

  const handleLogout = async () => {    
    localStorage.removeItem("token");
    sessionStorage.removeItem("user");
    
    window.location.href = "/login";
  };

  useEffect(() => {
    load();

    const intervalId = setInterval(() => {
      load();
    }, 2000);

    return () => clearInterval(intervalId);
  }, []);

  const handleUploadComplete = () => {
    load();
    setOpenUpload(false);
  };

  return (
    <Layout>
      <div className="flex justify-between mb-6">
        <h1 className="text-2xl font-semibold">Главная</h1>

        <div className="flex gap-3">
          <button
            onClick={load}
            className="bg-gray-700 px-4 py-2 rounded-lg hover:bg-gray-600 transition"
            title="refresh"
          >
            Обновить
          </button>
          <button
            onClick={() => setOpenUpload(true)}
            className="bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-500 transition"
          >
            Загрузить
          </button>
          <button
            onClick={() => handleLogout()}
            className="bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-500 transition"
          >
            Выйти
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {batches.length === 0 ? (
          <div className="col-span-3 text-center text-gray-400 py-8">
            Не найдено загрузок. Добавьте новую по кнопке "Загрузить"
          </div>
        ) : (
          batches.map((b) => (
            <div
              key={b.id}
              onClick={() => setSelected(b)}
              className="p-4 rounded-xl bg-[#161616] border border-gray-800 hover:border-gray-600 cursor-pointer transition"
            >
              <p className="text-sm text-gray-400">Выгрузка</p>
              <p className="text-lg">{b.id.slice(0, 8)}</p>

              <div className="mt-2 text-sm">
                <span
                  className={
                    b.status === "completed"
                      ? "text-green-400"
                      : b.status === "processing"
                      ? "text-blue-400"
                      : "text-yellow-400"
                  }
                >
                  {b.status === "completed" ? "выполнено" : b.status === "processing" ? "на проверке" : b.status}
                </span>
              </div>
              
              {b.total_files && (
                <div className="mt-1 text-xs text-gray-500">
                  Файлов: {b.total_files}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {openUpload && (
        <UploadModal 
          onClose={() => setOpenUpload(false)} 
          onUploadComplete={handleUploadComplete}
        />
      )}
      {selected && (
        <BatchModal batch={selected} onClose={() => setSelected(null)} />
      )}
    </Layout>
  );
}