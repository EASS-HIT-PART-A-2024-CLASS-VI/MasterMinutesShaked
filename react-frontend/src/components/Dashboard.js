import React, { useState } from 'react';
import TaskForm from './TaskForm';
import TaskList from './TaskList';
import ScheduleForm from './ScheduleForm';
import ScheduleViewer from './ScheduleViewer';
import api from '../services/api';
import { toast } from 'react-toastify';
import './Dashboard.css';
import logo from '../assets/iconback.png';
import telegramApi from '../services/telegramApi';

const Dashboard = ({ token, setToken }) => {
  const [tasks, setTasks] = useState([]);
  const [schedule, setSchedule] = useState(null);
  const [scheduleId, setScheduleId] = useState(null);
  const [activeTab, setActiveTab] = useState('tasks');

  const handleAddTask = (task) => {
    setTasks([...tasks, task]);
    toast.success(`Task "${task.name}" added!`);
  };

  const handleRemoveTask = (index) => {
    const newTasks = [...tasks];
    newTasks.splice(index, 1);
    setTasks(newTasks);
    toast.info('Task removed');
  };

  const handleCreateSchedule = async (scheduleData) => {
    try {
      console.log('Creating schedule with data:', scheduleData);
      const response = await api.post('/schedule', 
        {
          tasks: tasks,
          constraints: scheduleData.constraints,
          working_days: scheduleData.workingDays,
          start_hour_day: scheduleData.startHourDay,
          end_hour_day: scheduleData.endHourDay,
          Breaks: scheduleData.breaks
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      console.log('Schedule created:', response.data);
      setSchedule(response.data);
      setActiveTab('viewSchedule');
      toast.success('Schedule created successfully!');
      return response.data; // Return the response data
    } catch (error) {
      console.error('Schedule creation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to create schedule');
      return null;
    }
  };

  const handleFetchSchedule = async (scheduleId) => {
    try {
      console.log('Fetching schedule with ID:', scheduleId);
      const response = await api.get(`/schedule/${scheduleId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('Schedule fetched:', response.data);
      setSchedule(response.data);
      setActiveTab('viewSchedule');
      toast.success('Schedule fetched successfully!');
    } catch (error) {
      console.error('Fetch schedule error:', error);
      toast.error(error.response?.data?.detail || 'Failed to fetch schedule');
    }
  };

  const handleSendScheduleToTelegram = async (scheduleId) => {
    try {
      console.log('Sending schedule to Telegram with ID:', scheduleId);
      const response = await telegramApi.get(`/get_schedule/${scheduleId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(response.data.message);
    } catch (error) {
      console.error('Error sending schedule to Telegram:', error);
      toast.error(error.response?.data?.detail || 'Failed to send schedule to Telegram');
    }
  };

  const handleLogout = () => {
    setToken(null);
    toast.info('Logged out successfully');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <img src={logo} alt="App Logo" className="dashboard-logo" />
        <h1>Task Scheduler</h1>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </header>
      
      <div className="dashboard-tabs">
        <button 
          className={activeTab === 'tasks' ? 'active' : ''} 
          onClick={() => setActiveTab('tasks')}
        >
          Tasks
        </button>
        <button 
          className={activeTab === 'schedule' ? 'active' : ''} 
          onClick={() => setActiveTab('schedule')}
        >
          Create Schedule
        </button>
        <button 
          className={activeTab === 'fetchSchedule' ? 'active' : ''} 
          onClick={() => setActiveTab('fetchSchedule')}
        >
          Fetch Schedule
        </button>
        {schedule && (
          <button 
            className={activeTab === 'viewSchedule' ? 'active' : ''} 
            onClick={() => setActiveTab('viewSchedule')}
          >
            View Schedule
          </button>
        )}
      </div>
      
      <div className="dashboard-content">
        {activeTab === 'tasks' && (
          <div className="tasks-section">
            <div className="task-form-container">
              <TaskForm onAddTask={handleAddTask} />
            </div>
            <div className="task-list-container">
              <TaskList tasks={tasks} onRemoveTask={handleRemoveTask} />
            </div>
          </div>
        )}
        
        {activeTab === 'schedule' && (
          <ScheduleForm onCreateSchedule={handleCreateSchedule} />
        )}
        
        {activeTab === 'fetchSchedule' && (
          <div className="fetch-schedule-section">
            <h2>Fetch Existing Schedule</h2>
            <div className="fetch-form">
              <input 
                type="text" 
                placeholder="Enter Schedule ID"
                onChange={(e) => setScheduleId(e.target.value)}
              />
              <button onClick={() => handleFetchSchedule(scheduleId)}>Fetch Schedule</button>
              <button onClick={() => handleSendScheduleToTelegram(scheduleId)}>Send Schedule to Telegram</button> {/* Add this button */}
            </div>
          </div>
        )}
        
        {activeTab === 'viewSchedule' && schedule && (
          <ScheduleViewer schedule={schedule} />
        )}
      </div>
    </div>
  );
};

export default Dashboard;