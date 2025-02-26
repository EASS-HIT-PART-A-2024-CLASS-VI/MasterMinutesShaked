import React from 'react';
import './TaskList.css';

const TaskList = ({ tasks, onRemoveTask }) => {
  if (tasks.length === 0) {
    return (
      <div className="task-list-empty">
        <h2>Tasks to Schedule</h2>
        <p>No tasks added yet. Add a task to get started.</p>
      </div>
    );
  }

  return (
    <div className="task-list">
      <h2>Tasks to Schedule</h2>
      <div className="task-list-items">
        {tasks.map((task, index) => (
          <div key={index} className={`task-item priority-${task.priority.toLowerCase()}`}>
            <div className="task-header">
              <h3>{task.name}</h3>
              <button
                className="remove-task-btn"
                onClick={() => onRemoveTask(index)}
              >
                &times;
              </button>
            </div>
            <div className="task-details">
              <p><strong>Duration:</strong> {task.duration_minutes} minutes</p>
              <p><strong>Priority:</strong> {task.priority}</p>
              {task.notes && <p><strong>Notes:</strong> {task.notes}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskList;