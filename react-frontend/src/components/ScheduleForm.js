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
  const [breaks, setBreaks] = useState([]);
  const [newBreak, setNewBreak] = useState({ start: '12:00', end: '13:00' });
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

  const handleAddBreak = () => {
    if (newBreak.start && newBreak.end) {
      setBreaks([...breaks, { ...newBreak }]);
      setNewBreak({ start: '', end: '' });
    }
  };

  const handleRemoveBreak = (index) => {
    const updatedBreaks = [...breaks];
    updatedBreaks.splice(index, 1);
    setBreaks(updatedBreaks);
  };

  const updateBreakField = (field, value) => {
    setNewBreak({
      ...newBreak,
      [field]: value
    });
  };

  const generateBreaksJson = () => {
    return JSON.stringify(breaks, null, 2);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
   
    // Validate JSON input for constraints
    const isConstraintsValid = validateJson(constraintsJson, 'Constraints');
    
    if (!isConstraintsValid) {
      return;
    }
   
    onCreateSchedule({
      startHourDay,
      endHourDay,
      workingDays,
      constraints: JSON.parse(constraintsJson),
      breaks: breaks
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
          <label>Breaks</label>
          <div className="breaks-container">
            {breaks.length > 0 ? (
              <div className="breaks-list">
                {breaks.map((breakItem, index) => (
                  <div key={index} className="break-item">
                    <span>{breakItem.start} - {breakItem.end}</span>
                    <button 
                      type="button" 
                      className="remove-break-btn"
                      onClick={() => handleRemoveBreak(index)}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-breaks">No breaks added</p>
            )}
            
            <div className="add-break-form">
              <div className="break-time-inputs">
                <div className="form-group">
                  <label htmlFor="breakStart">Start</label>
                  <input
                    type="time"
                    id="breakStart"
                    value={newBreak.start}
                    onChange={(e) => updateBreakField('start', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="breakEnd">End</label>
                  <input
                    type="time"
                    id="breakEnd"
                    value={newBreak.end}
                    onChange={(e) => updateBreakField('end', e.target.value)}
                  />
                </div>
              </div>
              <button
                type="button"
                className="add-break-btn"
                onClick={handleAddBreak}
              >
                Add Break
              </button>
            </div>
          </div>
        </div>
       
        {jsonError && <div className="json-error">{jsonError}</div>}
       
        <button type="submit" className="create-schedule-btn">Create Schedule</button>
      </form>
    </div>
  );
};

export default ScheduleForm;