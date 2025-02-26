// src/components/ScheduleViewer.js
import React, { useState, useEffect } from 'react';
import { FaClock, FaCalendarAlt, FaStickyNote } from 'react-icons/fa';
import './ScheduleViewer.css';

const ScheduleViewer = ({ schedule }) => {
  const [currentWeek, setCurrentWeek] = useState([]);
  const [hoveredTask, setHoveredTask] = useState(null);
  
  useEffect(() => {
    if (schedule && Array.isArray(schedule.schedule) && schedule.schedule.length > 0) {
      // Get the week of the first task
      const firstTaskDate = new Date(schedule.schedule[0].date);
      generateWeekDays(firstTaskDate);
    }
  }, [schedule]);
  
  // Generate an array of 7 days starting from the given date's week
  const generateWeekDays = (date) => {
    const dayOfWeek = date.getDay();
    const diff = date.getDate() - dayOfWeek;
    const firstDay = new Date(date.setDate(diff));
    
    const weekDays = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(firstDay);
      day.setDate(firstDay.getDate() + i);
      weekDays.push(day);
    }
    
    setCurrentWeek(weekDays);
  };
  
  // Format date to display full day name and date
  const formatDay = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };
  
  // Format date string to YYYY-MM-DD
  const formatDateToYYYYMMDD = (date) => {
    const d = new Date(date);
    return d.toISOString().split('T')[0];
  };
  
  // Convert time string (HH:MM) to minutes since midnight
  const timeToMinutes = (timeStr) => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
  };
  
  // Get task position and height based on start and end times
  const getTaskPositionAndHeight = (task) => {
    const startMinutes = timeToMinutes(task.start_time);
    const endMinutes = timeToMinutes(task.end_time);
    const duration = endMinutes - startMinutes;
    
    // Calculate position from top (day starts at 6:00 AM = 360 minutes)
    const dayStartMinutes = 6 * 60; // 6 AM
    const dayRange = 16 * 60; // 16 hours (6 AM to 10 PM)
    
    const topPosition = ((startMinutes - dayStartMinutes) / dayRange) * 100;
    const heightPercentage = (duration / dayRange) * 100;
    
    return {
      top: `${topPosition}%`,
      height: `${heightPercentage}%`,
    };
  };
  
  // Get color class based on priority
  const getPriorityColorClass = (priority) => {
    switch(priority?.toLowerCase()) {
      case 'high':
        return 'priority-high';
      case 'medium':
        return 'priority-medium';
      case 'low':
        return 'priority-low';
      default:
        return 'priority-medium';
    }
  };
  
  // Format time to display properly (e.g., "09:00" instead of "9:00")
  const formatTime = (timeStr) => {
    return timeStr;
  };
  
  if (!schedule || !Array.isArray(schedule.schedule) || schedule.schedule.length === 0) {
    return <div className="schedule-viewer-empty">No schedule to display</div>;
  }
  
  // Generate time slots for the Y-axis (6:00 AM to 10:00 PM)
  const timeSlots = [];
  for (let i = 6; i <= 22; i++) {
    timeSlots.push(`${i}:00`);
  }
  
  // Organize tasks to avoid overlaps
  const organizeTasksForDay = (tasksForDay) => {
    if (!tasksForDay.length) return [];
    
    // Sort tasks by start time
    const sortedTasks = [...tasksForDay].sort((a, b) => 
      timeToMinutes(a.start_time) - timeToMinutes(b.start_time)
    );
    
    // Assign columns to avoid overlaps
    const columnAssignments = [];
    
    for (let i = 0; i < sortedTasks.length; i++) {
      const task = sortedTasks[i];
      const taskStart = timeToMinutes(task.start_time);
      const taskEnd = timeToMinutes(task.end_time);
      
      // Find the first available column
      let column = 0;
      while (true) {
        // Check if this column is available for this time slot
        const isColumnAvailable = !columnAssignments.some(assignment => {
          const assignedTask = assignment.task;
          const assignedColumn = assignment.column;
          
          if (assignedColumn !== column) return false;
          
          const assignedStart = timeToMinutes(assignedTask.start_time);
          const assignedEnd = timeToMinutes(assignedTask.end_time);
          
          // Check for overlap
          return (taskStart < assignedEnd && taskEnd > assignedStart);
        });
        
        if (isColumnAvailable) break;
        column++;
      }
      
      columnAssignments.push({ task, column });
    }
    
    return columnAssignments;
  };
  
  return (
    <div className="schedule-viewer">
      <div className="schedule-header">
        <h2>Schedule View</h2>
        {schedule.schedule_id && <div className="schedule-id">ID: {schedule.schedule_id}</div>}
      </div>
      
      <div className="calendar-container">
        {/* Time column */}
        <div className="time-column">
          <div className="time-header"></div>
          {timeSlots.map((time, index) => (
            <div key={index} className="time-slot">
              {time}
            </div>
          ))}
        </div>
        
        {/* Day columns */}
        {currentWeek.map((day, dayIndex) => {
          const dayStr = formatDateToYYYYMMDD(day);
          const tasksForDay = schedule.schedule.filter(task => task.date === dayStr);
          const organizedTasks = organizeTasksForDay(tasksForDay);
          
          // Calculate the maximum number of columns needed for this day
          const maxColumns = organizedTasks.length > 0 
            ? Math.max(...organizedTasks.map(t => t.column)) + 1 
            : 1;
          
          return (
            <div key={dayIndex} className="day-column">
              <div className="day-header">{formatDay(day)}</div>
              <div className="day-slots">
                {/* Time slots background */}
                {timeSlots.map((_, index) => (
                  <div key={index} className="day-time-slot"></div>
                ))}
                
                {/* Tasks */}
                {organizedTasks.map(({ task, column }, taskIndex) => {
                  const position = getTaskPositionAndHeight(task);
                  const colorClass = getPriorityColorClass(task.priority);
                  
                  // Calculate width and left position based on column assignment
                  const width = `calc(${100 / maxColumns}% - 6px)`;
                  const left = `calc(${(column * 100) / maxColumns}% + 3px)`;
                  
                  return (
                    <div
                      key={taskIndex}
                      className={`task-item ${colorClass}`}
                      style={{
                        ...position,
                        width,
                        left,
                        right: 'auto' // Override the 'right: 5px' from CSS
                      }}
                      onMouseEnter={() => setHoveredTask(task)}
                      onMouseLeave={() => setHoveredTask(null)}
                    >
                      <div className="task-time">
                        {formatTime(task.start_time)} - {formatTime(task.end_time)}
                      </div>
                      <div className="task-name">{task.task_name}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Task detail popup */}
      {hoveredTask && (
        <div className="task-detail-popup">
          <h3>{hoveredTask.task_name}</h3>
          <div className="task-detail-item">
            <FaClock />
            <span>{hoveredTask.start_time} - {hoveredTask.end_time}</span>
          </div>
          <div className="task-detail-item">
            <FaCalendarAlt />
            <span>{hoveredTask.day}, {hoveredTask.date}</span>
          </div>
          <div className="task-detail-item">
            <span className={`priority-badge ${getPriorityColorClass(hoveredTask.priority)}`}>
              {hoveredTask.priority}
            </span>
          </div>
          {hoveredTask.notes && (
            <div className="task-detail-item notes">
              <FaStickyNote />
              <span>{hoveredTask.notes}</span>
            </div>
          )}
          <div className="task-detail-item">
            <span>Task ID: {hoveredTask.task_id}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScheduleViewer;