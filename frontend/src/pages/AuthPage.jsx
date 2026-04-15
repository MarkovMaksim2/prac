import { useState } from "react";
import api from "../api/client";

export default function AuthPage({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = async () => {
    if (isRegister) {
      await api.post("/register", {
        email,
        password,
      });
    }

    const res = await api.post("/login", {
      email,
      password,
    });

    onLogin(res.data.access_token);
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gray-950 text-white">
      <div className="bg-gray-900 p-8 rounded-2xl w-96 shadow-xl">
        <h1 className="text-2xl mb-6">
          {isRegister ? "Регистрация" : "Вход"}
        </h1>

        <input
          className="w-full mb-3 p-2 rounded bg-gray-800"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="w-full mb-4 p-2 rounded bg-gray-800"
          placeholder="Пароль"
          type="password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={submit}
          className="w-full bg-blue-600 p-2 rounded hover:bg-blue-500"
        >
          {isRegister ? "Зарегистрироваться" : "Войти"}
        </button>

        <p
          className="mt-4 text-sm cursor-pointer text-gray-400"
          onClick={() => setIsRegister(!isRegister)}
        >
          {isRegister ? "Уже есть аккаунт?" : "Нет аккаунта?"}
        </p>
      </div>
    </div>
  );
}