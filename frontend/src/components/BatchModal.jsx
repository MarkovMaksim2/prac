import { useEffect, useState } from "react";
import api from "../api/client";

export default function BatchModal({ batch, onClose }) {
  const [data, setData] = useState(null);
  const [expandedRows, setExpandedRows] = useState({});
  const [loadingDelete, setLoadingDelete] = useState(false);

  useEffect(() => {
    api.get(`/batch/${batch.id}`).then((res) => setData(res.data));
  }, [batch.id]);

  const toggleRow = (fileId) => {
    setExpandedRows((prev) => ({
      ...prev,
      [fileId]: !prev[fileId],
    }));
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  const handleDelete = async () => {
    try {
      setLoadingDelete(true);
      await api.delete(`/batch/${batch.id}`);
      onClose();
    } catch (err) {
      console.error("Ошибка удаления:", err);
      alert("Не удалось удалить выгрузку.");
    } finally {
      setLoadingDelete(false);
    }
  };
  const [loadingDownload, setLoadingDownload] = useState(false);
  const handleDownload = async () => {
    try {
      setLoadingDownload(true);

      const res = await api.get(`/report/${batch.id}`, {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${batch.id}.xlsx`);

      document.body.appendChild(link);
      link.click();
      link.remove();

    } catch (err) {
      console.error("Ошибка скачивания:", err);
      alert("Не удалось скачать отчет");
    } finally {
      setLoadingDownload(false);
    }
  };


  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-[#161616] p-6 rounded-xl w-[800px] max-h-[80vh] overflow-y-auto border border-gray-800">
        <h2 className="mb-4 text-xl font-bold">Детали выгрузки</h2>

        {data && (
          <>
            <div className="mb-4 p-3 bg-gray-800/50 rounded-lg">
              <p>Статус: <span className="font-semibold">{data.status === "completed" ? "выполнено" : data.status === "processing" ? "на проверке" : data.status}</span></p>
              <p>Всего файлов: <span className="font-semibold">{data.total_files}</span></p>
            </div>

            {data.files && Object.keys(data.files).length > 0 ? (
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-2 px-3">Имя файла</th>
                    <th className="text-center py-2 px-3 w-[100px]">Оценка</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.files).map(([fileId, fileData]) => (
                    <>
                      <tr
                        key={fileId}
                        onClick={() => toggleRow(fileId)}
                        className="border-b border-gray-800 cursor-pointer hover:bg-gray-800/50 transition-colors"
                      >
                        <td className="py-2 px-3">
                          <span className="text-blue-400">
                            {fileData.name || fileId}
                          </span>
                        </td>
                        <td className={`py-2 px-3 text-center font-bold ${getScoreColor(fileData.score)}`}>
                          {fileData.score !== undefined ? fileData.score : "N/A"}
                        </td>
                      </tr>
                      {expandedRows[fileId] && fileData.errors && fileData.errors.length > 0 && (
                        <tr className="bg-gray-900/50">
                          <td colSpan="2" className="py-3 px-6">
                            <div className="text-sm">
                              <div className="font-semibold mb-2 text-gray-300">
                                Ошибок ({fileData.errors.length}):
                              </div>
                              <ul className="space-y-2">
                                {fileData.errors.map((error, idx) => (
                                  <li key={error.id || idx} className="border-l-2 border-red-500 pl-3 py-1">
                                    <div className="text-gray-300">
                                      {error.message}
                                    </div>
                                    {error.paragraph && (
                                      <div className="text-gray-500 text-xs mt-1">
                                        Параграф: {error.paragraph}
                                      </div>
                                    )}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-gray-400">No files found</p>
            )}
          </>
        )}
        <button
          onClick={handleDownload}
          disabled={data?.status !== "completed" || loadingDownload}
          className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition-colors disabled:opacity-50 mr-2"
        >
          {loadingDownload ? "Скачивание..." : "Скачать отчет"}
        </button>
        <button
            onClick={handleDelete}
            disabled={loadingDelete}
            className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition-colors disabled:opacity-50"
          >
            {loadingDelete ? "Удаление..." : "Удалить выгрузку"}
        </button>
        <button
          onClick={onClose}
          className="mt-6 bg-red-500 hover:bg-red-600 px-4 py-2 rounded transition-colors"
        >
          Закрыть
        </button>
      </div>
    </div>
  );
}