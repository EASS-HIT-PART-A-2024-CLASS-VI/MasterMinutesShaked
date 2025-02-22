import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import axios from "axios";
import "tailwindcss/tailwind.css";

const API_URL = "http://fastapi:1236";

const Login = ({ setToken }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await axios.post(`${API_URL}/token`, { username, password });
      setToken(response.data.access_token);
      navigate("/dashboard");
    } catch (error) {
      alert("Login failed. Please check your credentials.");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-96">
        <h2 className="text-2xl font-semibold text-center">Login</h2>
        <input
          type="text"
          placeholder="Username"
          className="w-full p-2 border rounded mt-4"
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full p-2 border rounded mt-2"
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          onClick={handleLogin}
          className="w-full bg-blue-500 text-white p-2 rounded mt-4 hover:bg-blue-600"
        >
          Login
        </button>
      </div>
    </div>
  );
};

const Dashboard = ({ token }) => {
  const [tasks, setTasks] = useState([]);
  const [taskName, setTaskName] = useState("");
  const [duration, setDuration] = useState(30);
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");

  const addTask = () => {
    if (!taskName || !date || !startTime) {
      alert("Please fill all fields.");
      return;
    }
    const startDateTime = `${date}T${startTime}`;
    const endDateTime = new Date(new Date(startDateTime).getTime() + duration * 60000).toISOString();
    const newTask = {
      title: taskName,
      start: startDateTime,
      end: endDateTime,
    };
    setTasks([...tasks, newTask]);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Task Scheduler</h1>
      <div className="bg-white p-4 rounded-lg shadow-md w-full mb-6">
        <h2 className="text-xl font-semibold">Add New Task</h2>
        <input
          type="text"
          placeholder="Task Name"
          className="w-full p-2 border rounded mt-2"
          onChange={(e) => setTaskName(e.target.value)}
        />
        <input
          type="date"
          className="w-full p-2 border rounded mt-2"
          onChange={(e) => setDate(e.target.value)}
        />
        <input
          type="time"
          className="w-full p-2 border rounded mt-2"
          onChange={(e) => setStartTime(e.target.value)}
        />
        <input
          type="number"
          placeholder="Duration (minutes)"
          className="w-full p-2 border rounded mt-2"
          onChange={(e) => setDuration(parseInt(e.target.value))}
        />
        <button
          onClick={addTask}
          className="w-full bg-green-500 text-white p-2 rounded mt-4 hover:bg-green-600"
        >
          Add Task
        </button>
      </div>
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        events={tasks}
        height="auto"
      />
    </div>
  );
};

const App = () => {
  const [token, setToken] = useState(null);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login setToken={setToken} />} />
        <Route path="/dashboard" element={token ? <Dashboard token={token} /> : <Login setToken={setToken} />} />
      </Routes>
    </Router>
  );
};

export default App;