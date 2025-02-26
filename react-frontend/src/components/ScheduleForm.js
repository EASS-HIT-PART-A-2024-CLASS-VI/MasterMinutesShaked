// src/components/ScheduleForm.js
import React, { useState } from 'react';
import './ScheduleForm.css';

const ScheduleForm = ({ onCreateSchedule }) => {
  const [startHourDay, setStartHourDay] = useState('09:00');
  const [endHourDay, setEndHourDay] = useState('17:00');
  const [workingDays, setWorkingDays] = useState([
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'
  ]);
  const [constraintsJson, setConstraintsJson] = useState('{}');
  const [breaksJson, setBreaksJson] = useState('[]');
  const [jsonError, setJsonError] = useState(null);

  const weekdays = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 
    'Thursday', 'Friday', 'Saturday'
  ];

  const handleWorkingDayToggle = (day) => {
    if (workingDays.includes(day)) {
      setWorkingDays(workingDays.filter(d => d !== day));
    } else {
      setWorkingDays([...workingDays, day]);
    }
  };

  const validateJson = (jsonString, fieldName) => {
    try {
      JSON.parse(jsonString);
      setJsonError(null);
      return true;
    } catch (error) {
      setJsonError(`Invalid JSON in ${fieldName}: ${error.message}`);
      return false;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate JSON inputs
    const isConstraintsValid = validateJson(constraintsJson, 'Constraints');
    const isBreaksValid = validateJson(breaksJson, 'Breaks');
    
    if (!isConstraintsValid || !isBreaksValid) {
      return;
    }
    
    onCreateSchedule({
      startHourDay,
      endHourDay,
      workingDays,
      constraints: JSON.parse(constraintsJson),
      breaks: JSON.parse(breaksJson)
    });
  };

  return (
    <div className="schedule-form">
      <h2>Scheduling Constraints</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="startHour">Start Hour of Day</label>
            <input
              type="time"
              id="startHour"
              value={startHourDay}
              onChange={(e) => setStartHourDay(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="endHour">End Hour of Day</label>
            <input
              type="time"
              id="endHour"
              value={endHourDay}
              onChange={(e) => setEndHourDay(e.target.value)}
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label>Working Days</label>
          <div className="working-days-select">
            {weekdays.map(day => (
              <div key={day} className="day-checkbox">
                <input
                  type="checkbox"
                  id={`day-${day}`}
                  checked={workingDays.includes(day)}
                  onChange={() => handleWorkingDayToggle(day)}
                />
                <label htmlFor={`day-${day}`}>{day}</label>
              </div>
            ))}
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="constraints">Constraints (JSON format)</label>
          <textarea
            id="constraints"
            value={constraintsJson}
            onChange={(e) => setConstraintsJson(e.target.value)}
            rows="4"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="breaks">Breaks (JSON format)</label>
          <textarea
            id="breaks"
            value={breaksJson}
            onChange={(e) => setBreaksJson(e.target.value)}
            rows="4"
          />
        </div>
        
        {jsonError && <div className="json-error">{jsonError}</div>}
        
        <button type="submit" className="create-schedule-btn">Create Schedule</button>
      </form>
    </div>
  );
};

export default ScheduleForm;